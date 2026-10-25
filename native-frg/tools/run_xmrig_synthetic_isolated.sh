#!/bin/sh
# Run only the disposable synthetic XMRig test. This wrapper creates a fresh
# Linux network namespace, then drops to an unprivileged user before starting
# either test process. Never use the normal host network as a fallback.
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Namespace setup requires a privileged test-environment launcher" >&2
    exit 2
fi
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 /path/to/xmrig /path/to/randomx_worker XMRIG_SHA256 WORKER_SHA256" >&2
    exit 2
fi
repository=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)

exec unshare --net -- /bin/sh -c '
    set -eu
    ip link set lo up
    # /sys/class/net can reflect the outer WSL sysfs mount even in a new
    # namespace. Query the live network namespace through netlink instead.
    if [ "$(ip -o link show | grep -Ec "^[0-9]+: ")" -ne 1 ] ||
       ! ip -o link show | grep -Eq "^[0-9]+: lo:"; then
        echo "Unexpected network interface in synthetic namespace" >&2
        exit 3
    fi
    if [ -n "$(ip -4 route show)" ] || [ -n "$(ip -6 route show)" ]; then
        echo "Network namespace has non-loopback routes" >&2
        exit 3
    fi

    # Only loopback is enabled. From this point onward the client and native
    # verifier run without root, supplementary groups, or Linux capabilities.
    cd /tmp/forgecoin-xmrig-run
    exec setpriv --reuid=65534 --regid=65534 --clear-groups \
        --inh-caps=-all --ambient-caps=-all --bounding-set=-all \
        --no-new-privs -- env \
        PYTHONPATH="$5" \
        python3 -m services.pool_research.tests.run_xmrig_synthetic \
        --xmrig "$1" --worker "$2" --xmrig-sha256 "$3" --worker-sha256 "$4"
' sh "$1" "$2" "$3" "$4" "$repository"
