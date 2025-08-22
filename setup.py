import os
import shutil

from skbuild import setup

skbuild_root = os.path.join(os.path.dirname(__file__), "_skbuild")
for root, dirs, files in os.walk(skbuild_root):
    for f in files:
        if f.startswith("libebur128") and f.endswith((".dylib", ".so", ".dll")):
            src_path = os.path.join(root, f)
            dst_dir = os.path.join("src", "loudstream", "lib")
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, f)
            print(f"Copying {src_path} -> {dst_path}")
            shutil.copy2(src_path, dst_path)

setup(
    name="loudstream",
    version="0.2.3",
    packages=["loudstream"],
    package_dir={"": "src"},
    cmake_install_dir="src/loudstream",
)
