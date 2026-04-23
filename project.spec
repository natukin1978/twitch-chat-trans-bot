# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 同梱するリソースの定義
added_files = [
    ('schema.json', '.'),
    ('templates/config.html', 'templates'),
    ('detail_schema.json', '.'),
    ('templates/detail_config.html', 'templates'),
]

# TwitchBot本体の設定
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
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

# 設定アプリの設定
b = Analysis(
    ['config_app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
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

# 詳細設定アプリの設定
c = Analysis(
    ['detail_config_app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
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

# 複数の実行ファイル間で共通のライブラリや依存関係を共有する設定
MERGE(
    (a, 'TwitchChatTransBot', 'TwitchChatTransBot'),
    (b, 'ConfigApp', 'ConfigApp'),
    (c, 'DetailConfigApp', 'DetailConfigApp')
)

# 各アプリのビルド設定
pyz_a = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe_a = EXE(
    pyz_a,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TwitchChatTransBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/main.ico',
)

pyz_b = PYZ(b.pure, b.zipped_data, cipher=block_cipher)
exe_b = EXE(
    pyz_b,
    b.scripts,
    [],
    exclude_binaries=True,
    name='ConfigApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/config_app.ico',
)

pyz_c = PYZ(c.pure, c.zipped_data, cipher=block_cipher)
exe_c = EXE(
    pyz_c,
    c.scripts,
    [],
    exclude_binaries=True,
    name='DetailConfigApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/config_app.ico',
)

# 全ての実行ファイルとバイナリを myapp_dist フォルダにまとめる
coll = COLLECT(
    exe_a,
    a.binaries,
    a.zipfiles,
    a.datas,
    exe_b,
    b.binaries,
    b.zipfiles,
    b.datas,
    exe_c,
    c.binaries,
    c.zipfiles,
    c.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='myapp_dist',
)
