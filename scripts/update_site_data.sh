#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_SOURCE="$PROJECT_ROOT/../泰康故事库_v260401.xlsx"

SOURCE_XLSX="${1:-$DEFAULT_SOURCE}"
DISPLAY_NAME="${2:-}"

echo "Updating story dashboard data..."
echo "Source Excel: $SOURCE_XLSX"

if [[ -n "$DISPLAY_NAME" ]]; then
  python3 "$SCRIPT_DIR/export_excel.py" "$SOURCE_XLSX" --display-name "$DISPLAY_NAME"
else
  python3 "$SCRIPT_DIR/export_excel.py" "$SOURCE_XLSX"
fi

echo "Done."
echo "Updated data file: $PROJECT_ROOT/data/story-data.js"
