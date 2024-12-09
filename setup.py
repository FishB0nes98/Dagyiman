import sys
from cx_Freeze import setup, Executable
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["pygame"],
    "excludes": [],
    "include_files": [
        ("assets", "assets"),  # Copy the entire assets folder
    ]
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Dagyiman",
    version="1.0",
    description="Dagyiman Game",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "dagyiman.py",
            base=base,
            target_name="Dagyiman.exe",
            icon="assets/player.png" if os.path.exists("assets/player.png") else None
        )
    ]
) 