#!/bin/sh
# Explicit source build only. Never runs XMRig or starts mining.
set -eu
source_dir=$(realpath "${1:?pinned upstream source checkout required}")
cd "$source_dir"
[ "$(git rev-parse HEAD)" = b2ca72480c58d197e18c885d9fc1a0c8d517e60a ]
python3 - <<'PY'
from pathlib import Path
import subprocess
allowed = {"src/donate.h"}
changed = set(subprocess.check_output(["git", "diff", "--name-only", "HEAD"], text=True).splitlines())
if changed - allowed:
    raise SystemExit("unexpected tracked source modifications")
p = Path("src/donate.h")
original = subprocess.check_output(["git", "show", "HEAD:src/donate.h"], text=True)
patched = original
for name in ("kDefaultDonateLevel", "kMinimumDonateLevel"):
    old = f"constexpr const int {name} = 1;"
    if original.count(old) != 1:
        raise SystemExit("unexpected donation source policy")
    patched = patched.replace(old, f"constexpr const int {name} = 0;")
if p.read_text() not in (original, patched):
    raise SystemExit("unexpected donation header modification")
p.write_text(patched)
PY
cmake -S . -B build-synthetic -DCMAKE_BUILD_TYPE=Release \
    -DWITH_HWLOC=OFF -DWITH_TLS=OFF -DWITH_HTTP=OFF -DWITH_MSR=OFF \
    -DWITH_OPENCL=OFF -DWITH_CUDA=OFF -DWITH_DMI=OFF -DWITH_ASM=OFF \
    -DWITH_BENCHMARK=OFF -DWITH_ENV_VARS=OFF -DWITH_EMBEDDED_CONFIG=OFF \
    -DWITH_CN_LITE=OFF -DWITH_CN_HEAVY=OFF -DWITH_CN_PICO=OFF \
    -DWITH_CN_FEMTO=OFF -DWITH_ARGON2=OFF -DWITH_KAWPOW=OFF -DWITH_GHOSTRIDER=OFF
cmake --build build-synthetic --parallel 2
git diff -- src/donate.h
sha256sum build-synthetic/xmrig-notls
readelf -d build-synthetic/xmrig-notls | grep NEEDED
printf 'Source build complete; executable has NOT been run. Synthetic isolated use only.\n'
