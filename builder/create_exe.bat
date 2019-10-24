@echo off

RD /S /Q ..\dist

move LabelTool.spec ..\src\LabelTool.spec

cd ..\src

python -m PyInstaller -w ..\src\LabelTool.spec

RD /S /Q build

move dist ..\dist

move LabelTool.spec ..\builder\LabelTool.spec

RD /S /Q __pycache__

