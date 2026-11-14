@echo off
rem Chạy dong-bo-view.py từ Task Scheduler (lịch "Nhip Cong Nghe - dong bo view", 21:30 mỗi ngày); kết quả ghi thêm vào pipeline\dong-bo-view.log
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
echo ==== %date% %time% >> dong-bo-view.log
"C:\Users\78\.local\bin\uv.exe" run python scripts\dong-bo-view.py >> dong-bo-view.log 2>&1
echo exit=%errorlevel% >> dong-bo-view.log
