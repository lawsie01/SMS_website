#!/usr/bin/env bash
# Build the single-file SPA preview.
#
# The viewer lazy-loads three.js through import(), which Vite emits as its own
# chunk. The preview re-runs page scripts as CLASSIC scripts on every route
# change, and a classic script cannot use import(). So for the preview build
# only, the loader is rewritten to STATIC imports: Vite then folds three.js
# into the viewer chunk and leaves no import statement behind. The source is
# restored on exit, committed or not.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SITE=$ROOT/site
VIEWER=$SITE/src/components/Product3DViewer.astro
WORK=$(mktemp -d)
OUT=${1:-$ROOT/sms-site-preview.html}
[ -d /opt/node22/bin ] && export PATH=/opt/node22/bin:$PATH

cp "$VIEWER" "$WORK/viewer.orig"
restore() { cp "$WORK/viewer.orig" "$VIEWER"; rm -rf "$WORK"; echo "viewer source restored"; }
trap restore EXIT

python3 - "$VIEWER" <<'PY'
import sys, re
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
old = re.search(r"  function loadThree\(\): Promise<void> \{.*?\n  \}\n", s, re.S).group(0)
new = '''  function loadThree(): Promise<void> {
    if (!threePromise) {
      THREE = _THREE;
      OrbitControls = _OrbitControls;
      GLTFLoader = _GLTFLoader;
      MeshoptDecoder = _MeshoptDecoder;
      threePromise = Promise.resolve();
    }
    return threePromise;
  }
'''
s = s.replace(old, new)
# Static imports so Vite inlines three.js into this chunk.
anchor = "  let THREE: typeof TT;"
s = s.replace(anchor,
  "  import * as _THREE from 'three';\n"
  "  import { OrbitControls as _OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';\n"
  "  import { GLTFLoader as _GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';\n"
  "  import { MeshoptDecoder as _MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';\n"
  + anchor)
open(p, 'w', encoding='utf-8').write(s)
print('viewer temporarily statically linked for the preview build')
PY

cd "$SITE"
npm run build 2>&1 | grep -E "^- [0-9]+ errors|Complete!" || true
python3 "$HERE/build_preview.py" "$OUT"
