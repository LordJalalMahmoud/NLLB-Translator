#!/usr/bin/env python3
"""
أداة تنزيل نموذج Meta NLLB-200 المكمم int8 لمرة واحدة (حوالي 600 ميجابايت).
"""
import sys
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("[ERROR] مكتبة huggingface_hub غير مثبتة.")
    print("يرجى تثبيتها أولاً عبر: pip install -r requirements.txt")
    sys.exit(1)


def download_nllb():
    base_dir = Path(__file__).resolve().parent
    target_dir = base_dir / "models" / "nllb-600m-ct2"
    model_bin = target_dir / "model.bin"

    if model_bin.exists():
        print(f"✅ نموذج Meta NLLB-200 مثبت ومتاح محلياً في:\n   {target_dir}")
        return True

    print("=" * 65)
    print("🚀 جاري تنزيل نموذج Meta NLLB-200 distilled 600M (CT2 int8)...")
    print("حجم التنزيل: حوالي 600 ميجابايت (يتم لمرة واحدة فقط ليعمل أوفلاين للأبد)")
    print("=" * 65)

    try:
        snapshot_download(
            repo_id="JustFrederik/nllb-200-distilled-600M-ct2-int8",
            local_dir=str(target_dir),
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
        )
        print("✅ تم تنزيل النموذج بنجاح وتثبيته محلياً!")
        return True
    except Exception as e:
        print(f"[ERROR] فشل التنزيل: {e}")
        return False


if __name__ == "__main__":
    download_nllb()
