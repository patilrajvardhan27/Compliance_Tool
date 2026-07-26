# PyInstaller spec for TUNBEEC Desktop.
#
# Must be built ON Windows (PyInstaller does not cross-compile). Run via build.bat,
# or let the "Build Windows Installer" GitHub Actions workflow do it in CI.
#
#   pyinstaller windows_exe/tunbeec.spec --distpath windows_exe/dist --workpath windows_exe/build
#
# Produces a "onedir" build at windows_exe/dist/TUNBEEC/TUNBEEC.exe -- everything the app
# needs (PySide6, the reference database, DOE-2.2 binaries, sample projects) lives next to
# the exe, and windows_exe/installer.iss wraps that folder into a single click-through
# Setup.exe installer.

import os

block_cipher = None

SRC_DIR = os.path.join(SPECPATH, "..", "python_tunbeec")
ICON = os.path.join(SRC_DIR, "resources", "image", "CU.ico")

a = Analysis(
    [os.path.join(SRC_DIR, "main.py")],
    pathex=[SRC_DIR],
    binaries=[],
    datas=[
        (os.path.join(SRC_DIR, "resources"), "resources"),
        (os.path.join(SRC_DIR, "PROJECT"), "PROJECT"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TUNBEEC",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TUNBEEC",
)
