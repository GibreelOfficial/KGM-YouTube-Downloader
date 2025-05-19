import os
import shutil
import subprocess
import sys

APP_NAME = "KGM YouTube Downloader"
SCRIPT_NAME = "main.py"
ICON_FILE = "icon.icns"
DATA_FILES = ["graphiti.png"]

def mac_add_data_format(file):
    return f"{file}:."  # macOS format: source:destination

def build():
    if not os.path.exists(SCRIPT_NAME):
        print(f"❌ ERROR: '{SCRIPT_NAME}' not found.")
        return

    # Build --add-data arguments
    data_args = []
    for file in DATA_FILES:
        if os.path.exists(file):
            data_args.append(f"--add-data={mac_add_data_format(file)}")
        else:
            print(f"⚠️ WARNING: Data file '{file}' not found.")

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",  # no console window
        "--onedir",    # make proper .app bundle
        f"--name={APP_NAME}",
        *data_args
    ]

    if os.path.exists(ICON_FILE):
        cmd.append(f"--icon={ICON_FILE}")
    else:
        print("⚠️ Icon file not found, skipping icon...")

    cmd.append(SCRIPT_NAME)

    print("🛠️ Building app with PyInstaller...\n")
    subprocess.run(cmd)

    # Move final .app to root directory
    app_bundle_path = os.path.join("dist", f"{APP_NAME}.app")
    if os.path.exists(app_bundle_path):
        final_path = f"./{APP_NAME}.app"
        if os.path.exists(final_path):
            shutil.rmtree(final_path)
        shutil.move(app_bundle_path, final_path)
        print(f"\n✅ App built: {final_path}")
    else:
        print("\n❌ Build failed — .app bundle not found in dist/.")

if __name__ == "__main__":
    build()
