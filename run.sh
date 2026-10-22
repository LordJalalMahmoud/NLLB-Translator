#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# استخدام بايثون والبيئة الافتراضية
if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON="$DIR/venv/bin/python3"
elif [ -f "/home/jalal/offline_translator/venv/bin/python3" ]; then
    PYTHON="/home/jalal/offline_translator/venv/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
else
    echo "Python 3 not found!"
    exit 1
fi

echo "========================================================="
echo "   🌟 تشغيل Meta NLLB-200 AI Translator (مشروع منفصل)"
echo "========================================================="

exec "$PYTHON" "$DIR/server.py" "$@"
