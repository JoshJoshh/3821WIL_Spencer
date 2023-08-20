# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
    ( 'C:/Users/User/AppData/Local/Programs/Python/Python311/Lib/site-packages/customtkinter', 'customtkinter/' ),
    ( 'C:/Users/User/Desktop/WIL/databases', 'databases' ),
    ( 'C:/Users/User/Desktop/WIL/assets', 'assets' ),
	( 'C:/Users/User/Desktop/WIL/mapping files', 'mapping files' )
]

a = Analysis(
    ['run.py'],
    pathex=["databases"],
    binaries=[],
    datas= added_files,
    hiddenimports=["popup", "backend"],
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
    name='CAEEPR Data Modeler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:/Users/User/Desktop/WIL/app_icon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
)
