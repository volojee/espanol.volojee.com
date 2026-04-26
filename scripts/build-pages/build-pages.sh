#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_DIR="$(realpath "$SCRIPT_DIR/../../src-md")"
OUTPUT_DIR="$(realpath -m "$SCRIPT_DIR/../../dist")"
PYTHON_SCRIPT="$SCRIPT_DIR/mkdocs_setup.py"

if ! command -v docker &>/dev/null; then
    echo "Ошибка: Docker не установлен или не в PATH. Установите Docker." >&2
    exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Создание папки входных файлов: $INPUT_DIR"
    mkdir -p "$INPUT_DIR"
fi

mkdir -p "$OUTPUT_DIR"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Ошибка: Файл $PYTHON_SCRIPT не найден. Положите его в одну папку с этим скриптом." >&2
    exit 1
fi

echo "🐳 Запуск Material for MkDocs в Docker..."
docker run --rm -it \
    -v "${INPUT_DIR}:/data/input:ro" \
    -v "${OUTPUT_DIR}:/data/output" \
    -v "${PYTHON_SCRIPT}:/app/mkdocs_setup.py:ro" \
    -w /app \
    --entrypoint /bin/sh \
    squidfunk/mkdocs-material:latest \
    -c "python /app/mkdocs_setup.py && mkdocs build -f /app/mkdocs.yml"

echo ""
echo "🎉 Успешно! Откройте: $OUTPUT_DIR/index.html"
echo "💡 Для локального просмотра: python3 -m http.server --directory '$OUTPUT_DIR'"
