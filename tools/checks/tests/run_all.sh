#!/bin/bash
# Runs every check's multi-direction test. Exits non-zero if any test fails.
#
# LOCAL DRIVER -- not shipped to consumers. precedent_materialize.py does not
# copy this file into a repo that resolves this source; it GENERATES its own
# tools/checks/tests/run_all.sh there, recorded in that repo's MANIFEST.json
# as "(generated)". This set had none until 2026-10-30, when universal's
# deep-check began running here and found nine tests nothing ran together.
set -uo pipefail
cd "$(dirname "$0")"
status=0
for t in test_*.sh; do
  [ -e "$t" ] || continue
  echo "--- $t ---"
  if ! bash "$t"; then
    status=1
  fi
done
exit $status
