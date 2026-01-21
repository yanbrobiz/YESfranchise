@echo off
REM Yes!加盟 自動化排程執行腳本
REM 請將此 .bat 檔案設定於 Windows 工作排程器

cd /d "%~dp0"
python auto_click.py
