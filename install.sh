#!/usr/bin/env bash
set -euo pipefail

echo "SysClean has been upgraded to use a Debian package (.deb) deployment system"
echo "to securely manage the privileged syscleand daemon via systemd."
echo ""
echo "Building the latest package..."
bash packaging/build_deb.sh

echo ""
echo "============================================================"
echo "Build complete! Please install the package using sudo:"
echo "  sudo dpkg -i packaging/sysclean_1.0.0_all.deb"
echo "============================================================"
echo ""