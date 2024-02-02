@echo off

set initialCompile=0
set noCompile=0
set copyTestData=0

if %noCompile% equ 0 (
call %~dp0..\env\Scripts\activate.bat
if %initialCompile% equ 0 (
python -m PyInstaller -y ^
--clean ^
--distpath %~dp0dist ^
--workpath %~dp0build ^
--upx-dir %~dp0upx-4.2.1-win64 ^
"Hunting Notes App.spec" 
) else (
::One directory mode, no overwrite warn, with upx compression, clean build/dist folders
::This will always fail to complete due to pythons recursion limit which requires you to add the following to the spec file
::import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
python -m PyInstaller -y -D ^
--clean ^
--distpath %~dp0dist ^
--workpath %~dp0build ^
--upx-dir %~dp0upx-4.2.1-win64 ^
--hidden-import sklearn.metrics._pairwise_distances_reduction._datasets_pair ^
--hidden-import sklearn.metrics._pairwise_distances_reduction._middle_term_computer ^
--hidden-import babel.numbers ^
#--add-data ultralytics;. ^
--name "Hunting Notes App" ^
..\src\hunting_notes_app.py 
)
::deactivate the virtual enviornment
call %~dp0..\env\Scripts\deactivate.bat
)

::Go to the distribution folder
cd dist/"Hunting Notes App"

::Create data folder for image annotator
md "Annotator Data"
md "Annotator Data"\"unannotated_images"
md "Annotator Data"\"annotated_images"
md "Annotator Data"\"annotated_images"\images
md "Annotator Data"\"annotated_images"\labels

::Copy in the yolov8 model so we don't have to download it
copy %~dp0..\src\yolov8n.pt %~dp0dist\"Hunting Notes App"
copy %~dp0..\src\settings.txt %~dp0dist\"Hunting Notes App"
copy %~dp0..\src\species.txt %~dp0dist\"Hunting Notes App"

::Create the models folder structure
md Models
md Models\"Detector Data"
md Models\"Detector Data"\dataset
md Models\"Detector Data"\runs

md "Resources"

::Create logs folder
md Logs

::Create finder models folder
md Models\"Finder Models"

xcopy /s /e /q %~dp0..\src\animal_detector\Models\"Detector Data"\dataset %~dp0dist\"Hunting Notes App"\Models\"Detector Data"\dataset
xcopy /s /e %~dp0..\src\Resources %~dp0dist\"Hunting Notes App"\Resources

if %copyTestData% equ 1 (
md %~dp0dist\"Hunting Notes App"\src\"Property Data"
xcopy /s /e %~dp0..\src\"Property Data" %~dp0dist\"Hunting Notes App"\"Property Data"
) else (
md %~dp0dist\"Hunting Notes App"\"Property Data"
)

pause