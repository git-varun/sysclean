#!/usr/bin/env bash
set -euo pipefail

echo "SysClean uses a Debian package (.deb) deployment system"
echo "to install the CLI tools into your environment."
echo ""
echo "Building the latest package..."
bash packaging/build_deb.sh

echo ""
echo "============================================================"
echo "Build complete! Please install the package using sudo:"
echo "  sudo dpkg -i packaging/sysclean_1.0.0_all.deb"
echo "============================================================"
echo ""