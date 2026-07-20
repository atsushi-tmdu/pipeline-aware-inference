#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")"
  pwd
)"

cd "$SCRIPT_DIR"

python fig1_framework_final.py
python fig2_type1_error_final.py
python fig3_power_final.py
python fig4_effective_search_final.py
python fig5_support2_final.py

echo "Done."
echo "Outputs are in:"
echo "$SCRIPT_DIR/output"
