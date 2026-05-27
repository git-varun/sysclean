#!/usr/bin/env bash
set -euo pipefail

VERSION="1.0.0"
PACKAGE_NAME="sysclean_${VERSION}_all"
BUILD_DIR="packaging/${PACKAGE_NAME}"

echo "Preparing build directory: ${BUILD_DIR}"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}/usr/local/bin"
mkdir -p "${BUILD_DIR}/usr/local/share/sysclean"
mkdir -p "${BUILD_DIR}/etc/sysclean"

# Copy DEBIAN metadata
cp -r packaging/DEBIAN "${BUILD_DIR}/"

# Copy binaries
cp bin/sysclean "${BUILD_DIR}/usr/local/bin/"
cp bin/syscleand "${BUILD_DIR}/usr/local/bin/"
chmod +x "${BUILD_DIR}/usr/local/bin/sysclean"
chmod +x "${BUILD_DIR}/usr/local/bin/syscleand"

# Copy python libraries, plugins, and UI assets
cp -r python "${BUILD_DIR}/usr/local/share/sysclean/"
cp -r modules "${BUILD_DIR}/usr/local/share/sysclean/"

cp requirements.txt "${BUILD_DIR}/usr/local/share/sysclean/"
mkdir -p "${BUILD_DIR}/usr/local/share/sysclean/ui"
cp -r ui/dist "${BUILD_DIR}/usr/local/share/sysclean/ui/"

# Ensure maintainer scripts are executable
chmod 755 "${BUILD_DIR}/DEBIAN/postinst" || true
chmod 755 "${BUILD_DIR}/DEBIAN/prerm" || true


# Adjust ROOT_DIR in binaries
sed -i 's|ROOT_DIR=.*|ROOT_DIR="/usr/local/share/sysclean"|g' "${BUILD_DIR}/usr/local/bin/sysclean"
sed -i 's|ROOT_DIR=.*|ROOT_DIR="/usr/local/share/sysclean"|g' "${BUILD_DIR}/usr/local/bin/syscleand"


# Copy config
if [ -f "config/default.yml" ]; then
    cp config/default.yml "${BUILD_DIR}/etc/sysclean/"
fi

echo "Building package..."
dpkg-deb --build "${BUILD_DIR}"

echo "Package built: packaging/${PACKAGE_NAME}.deb"
