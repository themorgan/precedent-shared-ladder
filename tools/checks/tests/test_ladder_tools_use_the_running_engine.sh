#!/usr/bin/env bash
# practice: upstream-review -- claims this test, so a consuming repository receives it
# The ladder's tools, loaded into the engine's own process, use the engine
# that process runs on and never put this set's tools/ in front of it.
# 2026-10-31: BestPractice's harness loaded upstream_review.py in-process; it
# put this set's tools/ first while importing, and leak_gate came from the
# set's older vendored copy for the rest of the run, turning a later test red.
# A planted "running engine" folder sits first on sys.path with its own
# leak_gate; each tool is imported, and the path and the module are checked.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LADDER="$HERE/../../ladder"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/eng"
echo 'WHO = "running engine"' > "$tmp/eng/leak_gate.py"
printf 'import leak_gate\nWHO = leak_gate.WHO\n' > "$tmp/eng/zz_probe.py"
python3 - "$tmp/eng" "$LADDER" <<'PY'
import importlib.util, sys
eng, ladder = sys.argv[1], sys.argv[2]
sys.path.insert(0, eng)
bad = []
def load(name):
    spec = importlib.util.spec_from_file_location(f'_ladder_{name}', f'{ladder}/{name}.py')
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:                                  # noqa: BLE001
        bad.append(f'{name}.py would not load: {type(e).__name__}: {e}')
        return None
    if sys.path[0] != eng:
        bad.append(f'{name}.py put {sys.path[0]} in front of the running engine')
    return mod
ur = load('upstream_review')
if ur is not None:
    probe = ur._engine('zz_probe')
    if getattr(probe, 'WHO', None) != 'running engine':
        bad.append("upstream_review._engine loaded a module whose imports came "
                   "from this set's tools/, not the running engine")
    if getattr(sys.modules.get('leak_gate'), 'WHO', None) != 'running engine':
        bad.append("leak_gate in this process is not the running engine's")
load('branch_page_note')
load('others_did')
for b in bad:
    print('FAIL:', b)
sys.exit(1 if bad else 0)
PY
rc=$?
[ "$rc" = 0 ] && echo "PASS: ladder tools use the running engine"
exit "$rc"
