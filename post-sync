#!/bin/bash
# This script automates the setup of a Yocto build environment after a 'repo sync'.

set -e # Exit immediately if any command fails

echo "--- [Cluster Hook] Starting post-sync Yocto environment configuration ---"

# --- 1. Initialize the build directory at the top level ---
# We will create a directory named 'build-rpi' at the root of the repo checkout.
# Then, we tell the oe-init-build-env script to use this directory.
TOP_DIR=$(pwd)
BUILD_DIR="${TOP_DIR}/build-rpi"

echo "[Cluster Hook] Initializing build directory at: ${BUILD_DIR}"
source sources/poky/oe-init-build-env "${BUILD_DIR}"

# The BDIR variable is now set to the path we provided.
# Sanity check to ensure it's correct.
if [ -z "$BDIR" ] || [ "$BDIR" != "$BUILD_DIR" ]; then
    echo "[Cluster Hook] ERROR: Build directory was not set correctly. Aborting."
    exit 1
fi

# --- 2. Configure local.conf ---
# The rest of the script works exactly the same, as BDIR points to the correct location.
echo "[Cluster Hook] Configuring conf/local.conf..."
# Check if the config block already exists to prevent adding it multiple times
if ! grep -q "# --- Custom settings added by cluster-hooks ---" "${BDIR}/conf/local.conf"; then
    cat >> "${BDIR}/conf/local.conf" <<EOF

# --- Custom settings added by cluster-hooks ---
MACHINE = "raspberrypi5-64"
ENABLE_UART = "1"
ENABLE_I2C = "1"
KERNEL_MODULE_AUTOLOAD:rpi += "i2c-dev i2c-bcm2708"
MACHINE_FEATURES:append = " vc4graphics"
DISTRO = "hehos"

# Enable RDP backend for Weston compositor
PACKAGECONFIG:append:pn-weston = " rdp"
# --- End of custom settings ---
EOF
else
    echo "[Cluster Hook] Custom settings already exist in local.conf. Skipping."
fi


# --- 3. Configure bblayers.conf ---
# The bitbake-layers script will use the correct BDIR path automatically.
echo "[Cluster Hook] Configuring conf/bblayers.conf..."
bitbake-layers add-layer "${TOP_DIR}/sources/meta-openembedded/meta-oe"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-openembedded/meta-python"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-openembedded/meta-networking"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-openembedded/meta-multimedia"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-raspberrypi"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-qt6"
bitbake-layers add-layer "${TOP_DIR}/sources/meta-coda-distro"


echo "--- [Cluster Hook] Yocto environment setup is complete! ---"
echo "Your build directory is 'build-rpi'."
echo "To use it, run: source sources/poky/oe-init-build-env build-rpi"
