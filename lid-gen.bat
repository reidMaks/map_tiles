@echo off
setlocal enabledelayedexpansion

set "source_dir=stl"
set "output_dir=lids"

if not exist "%output_dir%" mkdir "%output_dir%"

for %%f in ("%source_dir%\*.stl") do (
    set "input_file=%%f"
    set "output_file=!input_file:%source_dir%=%output_dir%!"
    set "output_file=!output_file!.stl"


    echo Обробка: !input_file!
    "C:\Program Files\OpenSCAD\openscad.exe" -o "!output_file!" -D path_to_stl="!input_file!" create_lid.scad
    echo Згенеровано файл: !output_file!
)

echo Обробка завершена.
