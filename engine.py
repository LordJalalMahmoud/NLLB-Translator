"""
محرك الترجمة المتقدم القائم على نموذج Meta NLLB-200 (No Language Left Behind)
- يعتمد على CTranslate2 بتكميم int8 لتشغيل فائق السرعة وأقل استهلاك للرام
- يدعم الفصحى الحديثة (arb_Arab) واللهجة المصرية (arz_Arab) والشامية (apc_Arab)
- يدعم المقارنة المباشرة مع نموذج Argos Translate القديم لتوضيح الفارق
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import ctranslate2
    from transformers import AutoTokenizer
except ImportError as e:
    raise ImportError(f"Missing dependency: {e}")

from arabizi import arabic_to_arabizi


class NllbTranslationEngine:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.model_dir = self.base_dir / "models" / "nllb-600m-ct2"
        model_bin = self.model_dir / "model.bin"

        # التحقق من وجود النموذج وتنزيله تلقائياً إن لم يكن موجوداً
        if not model_bin.exists():
            from download_model import download_nllb
            download_nllb()

        print("[NLLB INIT] جاري تحميل معالج الرموز Tokenizer لنموذج NLLB-200...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir), src_lang="eng_Latn")

        print("[NLLB INIT] جاري تهيئة محرك CTranslate2 لنموذج Meta NLLB-200...")
        self.translator = ctranslate2.Translator(
            str(self.model_dir),
            device="cpu",
            compute_type="int8",
            inter_threads=2,
            intra_threads=2,
        )
        self.translator_lock = threading.Lock()

        # فحص إمكانية تحميل نموذج Argos القديم لأغراض المقارنة
        self.argos_translator = None
        self.argos_sp = None
        self._init_argos_legacy()

    def _init_argos_legacy(self):
        """تهيئة النموذج القديم (إن وجد) لإظهار مقارنة حية بين النموذجين."""
        argos_path = Path.home() / ".local/share/argos-translate/packages/en_ar"
        if (argos_path / "model/model.bin").exists() and (argos_path / "sentencepiece.model").exists():
            try:
                import sentencepiece as spm
                self.argos_sp = spm.SentencePieceProcessor(model_file=str(argos_path / "sentencepiece.model"))
                self.argos_translator = ctranslate2.Translator(
                    str(argos_path / "model"),
                    device="cpu",
                    compute_type="int8",
                )
                print("[ARGOS LEGACY] تم تحميل النموذج القديم للمقارنة بنجاح.")
            except Exception as e:
                print(f"[ARGOS LEGACY WARNING] {e}")

    def translate_nllb(self, text: str, target_lang: str = "arb_Arab") -> Tuple[str, float]:
        """
        الترجمة عبر Meta NLLB-200:
        - arb_Arab: عربي فصحى
        - arz_Arab: لهجة مصرية (عامية)
        - apc_Arab: لهجة شامية
        """
        clean_text = text.strip()
        if not clean_text:
            return "", 0.0

        t0 = time.perf_counter()

        # 1. الترميز
        source_tokens = self.tokenizer.convert_ids_to_tokens(
            self.tokenizer.encode(clean_text)
        )

        # 2. بادئة اللغة المستهدفة
        target_prefix = [target_lang]

        # 3. الترجمة عبر محرك CTranslate2 (beam_size=1 لأقصى سرعة واستجابة سريعة)
        with self.translator_lock:
            results = self.translator.translate_batch(
                [source_tokens],
                target_prefix=[target_prefix],
                beam_size=1,
                max_batch_size=32,
            )

        # 4. فك الترميز
        hypothesis = results[0].hypotheses[0]
        # إزالة بادئة اللغة
        if hypothesis and hypothesis[0] == target_lang:
            hypothesis = hypothesis[1:]

        sub_ids = self.tokenizer.convert_tokens_to_ids(hypothesis)
        translated_text = self.tokenizer.decode(sub_ids, skip_special_tokens=True).strip()

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return translated_text, elapsed_ms

    def translate_argos(self, text: str) -> Optional[str]:
        """الترجمة عبر النموذج القديم (Argos) لتوليد المقارنة."""
        if not self.argos_translator or not self.argos_sp:
            return None

        clean_text = text.strip()
        if not clean_text:
            return ""

        try:
            tokens = [self.argos_sp.encode(clean_text, out_type=str)]
            results = self.argos_translator.translate_batch(tokens, beam_size=1)
            ar_text = self.argos_sp.decode_pieces(results[0].hypotheses[0]).replace("▁", " ").strip()
            return ar_text
        except Exception:
            return None

    def translate_full_comparison(self, text: str) -> dict:
        """ترجمة النص بجميع الخيارات لمقارنة الجودة في شاشة واحدة."""
        # 1. NLLB فصحى
        nllb_standard, nllb_time = self.translate_nllb(text, target_lang="arb_Arab")

        # 2. NLLB مصري (عامية)
        nllb_egyptian, _ = self.translate_nllb(text, target_lang="arz_Arab")

        # 3. فرانكو مشتق من فصحى NLLB
        franco = arabic_to_arabizi(nllb_standard)

        # 4. ترجمة النموذج القديم للمقارنة
        old_argos = self.translate_argos(text)

        return {
            "original": text,
            "nllb_standard": nllb_standard,
            "nllb_egyptian": nllb_egyptian,
            "franco": franco,
            "legacy_argos": old_argos,
            "nllb_elapsed_ms": nllb_time,
        }
