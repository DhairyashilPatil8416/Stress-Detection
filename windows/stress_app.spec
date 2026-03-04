# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Add cv2 data files (Haar cascades)
datas = [
    ('C:\\Stress-Detection\\.venv\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml', 'cv2/data/'),
    ('C:\\Stress-Detection\\stress_cnn_model.h5', 'stress_cnn_model.h5'),  # Add model file; adjust path if different
    ('C:\\Stress-Detection\\windows\\.env', '.env'),  # Add environment file
]

binaries = []
hiddenimports = ['win10toast']  # Add win10toast for notifications
tmp_ret = collect_all('tensorflow')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['stress_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    collect_all=['tensorflow'],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='stress_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Change to False to hide console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:\\Stress-Detection\\windows\\icon.ico',  # Add this line for the icon
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='stress_app',
)
