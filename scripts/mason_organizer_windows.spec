# PyInstaller spec for Mason Organizer Windows build.

from pathlib import Path

block_cipher = None
root = Path.cwd()


a = Analysis(
    ['main.py'],
    pathex=[str(root)],
    binaries=[],
    datas=[('assets', 'assets'), ('src/resources', 'src/resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Mason Organizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icons/mason-organizer-icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Mason Organizer',
)
