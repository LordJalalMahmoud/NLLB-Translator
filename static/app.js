document.addEventListener("DOMContentLoaded", () => {
  const inputEl = document.getElementById("inputEnglish");
  const btnTranslate = document.getElementById("btnTranslate");

  const outStandard = document.getElementById("outStandard");
  const outEgyptian = document.getElementById("outEgyptian");
  const outFranco = document.getElementById("outFranco");
  const outArgos = document.getElementById("outArgos");
  const timeBadge = document.getElementById("timeBadge");

  // Theme
  document.getElementById("themeToggle").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") || "dark";
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
  });

  // Samples
  document.querySelectorAll(".sample-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      inputEl.value = btn.dataset.sample;
      doTranslate();
    });
  });

  btnTranslate.addEventListener("click", doTranslate);

  inputEl.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
      e.preventDefault();
      doTranslate();
    }
  });

  async function doTranslate() {
    const text = inputEl.value.trim();
    if (!text) return;

    btnTranslate.disabled = true;
    btnTranslate.textContent = "جاري الترجمة بالذكاء الاصطناعي...";

    try {
      const resp = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });

      const data = await resp.json();
      outStandard.textContent = data.nllb_standard || "---";
      outEgyptian.textContent = data.nllb_egyptian || "---";
      outFranco.textContent = data.franco || "---";
      outArgos.textContent = data.legacy_argos || "(النموذج القديم غير متوفر)";
      timeBadge.textContent = `⚡ وقت استجابة NLLB: ${data.nllb_elapsed_ms}ms`;
    } catch (e) {
      alert("خطأ: " + e.message);
    } finally {
      btnTranslate.disabled = false;
      btnTranslate.textContent = "ترجمة بالذكاء الاصطناعي NLLB-200";
    }
  }

  // Copy buttons
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.target;
      const text = document.getElementById(targetId).textContent;
      if (text && text !== "---") {
        navigator.clipboard.writeText(text);
        btn.textContent = "تم النسخ ✓";
        setTimeout(() => btn.textContent = "نسخ", 1500);
      }
    });
  });

  // Auto-translate initial sample
  doTranslate();
});
