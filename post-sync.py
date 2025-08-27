#!/usr/bin/env python3
#
# This script automates the setup of a Yocto build environment after a 'repo sync'.
# It configures the build, adds layers, and pre-fetches source code.
#

import os
import subprocess
import sys

# --- Configuration ---
TOP_DIR = os.getcwd()
BUILD_DIR_NAME = "build-rpi"
BUILD_DIR = os.path.join(TOP_DIR, BUILD_DIR_NAME)

LOCAL_CONF_SETTINGS = f"""
# --- Custom settings added by cluster-hooks ---
MACHINE = "raspberrypi5"
ENABLE_UART = "1"
ENABLE_I2C = "1"
KERNEL_MODULE_AUTOLOAD:rpi += "i2c-dev i2c-bcm2708"
MACHINE_FEATURES:append = " vc4graphics"
DISTRO = "hehos"

# Enable RDP backend for Weston compositor
PACKAGECONFIG:append:pn-weston = " rdp"
# --- End of custom settings ---
"""

LAYERS_TO_ADD = [
    "sources/meta-openembedded/meta-oe",
    "sources/meta-openembedded/meta-python",
    "sources/meta-openembedded/meta-networking",
    "sources/meta-openembedded/meta-multimedia",
    "sources/meta-raspberrypi",
    "sources/meta-qt6",
    "sources/meta-coda",
]

def run_command(cmd, cwd=None):
    """Helper function to run a shell command."""
    print(f"[Cluster Hook] Running command: {cmd}")
    try:
        # 'source' requires running in a shell.
        is_sourcing = "source" in cmd
        subprocess.run(
            cmd,
            check=True,
            shell=is_sourcing,
            executable='/bin/bash' if is_sourcing else None,
            cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        print(f"[Cluster Hook] ERROR: Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

def main(**kwargs):
    """Main function to execute the setup process."""
    print(f"[Cluster Hook] Hook called with arguments: {kwargs}")
    print("--- [Cluster Hook] Starting post-sync Yocto environment configuration (Python) ---")

    # --- 1. Initialize the build directory ---
    init_script = os.path.join(TOP_DIR, "sources/poky/oe-init-build-env")
    print(f"[Cluster Hook] Initializing build directory at: {BUILD_DIR}")
    run_command(f"source {init_script} {BUILD_DIR}", cwd=TOP_DIR)
    print(f"[Cluster Hook] Build directory is at: {BUILD_DIR}")

    # --- 2. Configure local.conf ---
    local_conf_path = os.path.join(BUILD_DIR, "conf/local.conf")
    print(f"[Cluster Hook] Configuring {local_conf_path}...")
    try:
        with open(local_conf_path, "r+") as f:
            content = f.read()
            if "# --- Custom settings added by cluster-hooks ---" not in content:
                f.write(LOCAL_CONF_SETTINGS)
                print("[Cluster Hook] Custom settings appended to local.conf.")
            else:
                print("[Cluster Hook] Custom settings already exist in local.conf. Skipping.")
    except FileNotFoundError:
        print(f"[Cluster Hook] ERROR: local.conf not found at {local_conf_path}", file=sys.stderr)
        sys.exit(1)

    # --- 3. Configure bblayers.conf ---
    print("[Cluster Hook] Configuring conf/bblayers.conf...")
    for layer in LAYERS_TO_ADD:
        layer_path = os.path.join(TOP_DIR, layer)
        # Each bitbake-layers command needs the build environment to be sourced.
        cmd = f"source {init_script} {BUILD_DIR} && bitbake-layers add-layer {layer_path}"
        run_command(cmd, cwd=TOP_DIR)

    print("[Cluster Hook] Pre-fetching all source code for the image...")
    # This command also needs the full build environment to be sourced.
    fetch_cmd = f"source {init_script} {BUILD_DIR} && bitbake core-image-coda-cluster --runonly=fetch"
    run_command(fetch_cmd, cwd=TOP_DIR)

    print("--- [Cluster Hook] Yocto environment setup and source fetching is complete! ---")
    print(f"Your build directory is '{BUILD_DIR_NAME}'.")
    print(f"To use it, run: source sources/poky/oe-init-build-env {BUILD_DIR_NAME}")

if __name__ == "__main__":
    main()
