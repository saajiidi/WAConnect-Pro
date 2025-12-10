@echo off
pushd "%~dp0.."
pip install pyinstaller
python -m PyInstaller --name WAConnectPro --onefile --add-data "templates;templates" app.py
