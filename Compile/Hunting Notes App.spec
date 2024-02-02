# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None
enableUPX = False


#Hunting Notes App
huntingNotes = Analysis(
    ['..\\src\\hunting_notes_app.py'],
    pathex=[],
    binaries=[],
    datas=[('../env/Lib/site-packages/ultralytics','./ultralytics')],
    hiddenimports=['sklearn.metrics._pairwise_distances_reduction._datasets_pair', 
					'sklearn.metrics._pairwise_distances_reduction._middle_term_computer', 
					'babel.numbers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
huntingNotesPyz = PYZ(huntingNotes.pure, huntingNotes.zipped_data, cipher=block_cipher)

#Image Annotator App
ImageAnnotator = Analysis(
    ['C:\\Users\\hanso\\Desktop\\ImageAnnotator\\AnnotatorApp.py'],
    pathex=['C:\\Users\\hanso\\Desktop\\ImageAnnotator'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
ImageAnnotatorPyz = PYZ(ImageAnnotator.pure)

merge = MERGE((huntingNotes, 'hunting_notes_app','"Hunting Notes'),
			(ImageAnnotator,'AnnotatorApp','Image Annotator'))
			
huntingNotesExe = EXE(
    huntingNotesPyz,
    huntingNotes.scripts,
    [],
    exclude_binaries=True,
    name='Hunting Notes App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=enableUPX,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

ImageAnnotatorExe = EXE(
    ImageAnnotatorPyz,
    ImageAnnotator.scripts,
    [],
    exclude_binaries=True,
    name='Image Annotator App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=enableUPX,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    huntingNotesExe,
    huntingNotes.binaries,
    huntingNotes.zipfiles,
    huntingNotes.datas,
	ImageAnnotatorExe,
    ImageAnnotator.binaries,
    ImageAnnotator.datas,
    strip=False,
    upx=enableUPX,
    upx_exclude=[],
    name='Hunting Notes App',
)

