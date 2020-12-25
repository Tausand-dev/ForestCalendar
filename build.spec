# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Rutherford\\Documents\\ForestCalendar'],
             binaries=[],
             datas=[('v44k1q05.img', ".")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ForestCalendar',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon="icon.ico", version='fileversion.txt')
