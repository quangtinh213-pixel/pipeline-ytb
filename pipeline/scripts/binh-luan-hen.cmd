@echo off
chcp 65001 >nul
rem Đăng bình luận mở đầu lên một video đã công khai, chạy một lần từ Task Scheduler (video riêng tư thì API trả 403).
rem Tham số 1 = video id, tham số 2 = tệp chữ UTF-8 (đường dẫn tính từ thư mục pipeline). Kết quả ghi thêm vào pipeline\binh-luan-hen.log
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
echo ==== %date% %time% %1 >> binh-luan-hen.log
"C:\Users\78\.local\bin\uv.exe" run python -c "import sys; from pathlib import Path; from tttc import dang; print(dang.binh_luan_ghim(dang.client(), sys.argv[1], Path(sys.argv[2]).read_text(encoding='utf-8').strip()))" %1 %2 >> binh-luan-hen.log 2>&1
set KQ=%errorlevel%
echo exit=%KQ% >> binh-luan-hen.log
if not "%KQ%"=="0" msg * "Nhip Cong Nghe: dang binh luan %1 LOI (exit %KQ%), xem pipeline\binh-luan-hen.log"
