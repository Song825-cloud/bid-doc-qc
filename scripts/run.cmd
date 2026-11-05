@echo off
cd /d "%~dp0.."

rem ============================================================
rem  Interpreter auto-detect:
rem  probes each candidate with "import docx" and uses the first that works.
rem  Override by setting BID_QC_PY to a full python.exe path (no spaces).
rem ============================================================
set "PY="
if defined BID_QC_PY call :probe "%BID_QC_PY%"
if not defined PY call :probe "python"
if not defined PY call :probe "py -3.12"
if not defined PY call :probe "py -3.11"
if not defined PY call :probe "py"

if not defined PY (
  echo [ERROR] No usable Python found ^(needs python-docx^).
  echo.
  echo   Install dependencies with:
  echo       pip install python-docx pywin32 pymupdf
  echo   Then re-run this file. If Python is installed but not on PATH,
  echo   set BID_QC_PY to the full path of python.exe before running.
  echo.
  pause
  exit /b 1
)

echo Using Python: %PY%
echo ============================================================
echo   Bid document QC workflow
echo.
echo    [1] Fast rebuild + assertions       (~5 sec, daily use)
echo    [2] Re-locate pages after edit      (~5 min)
echo    [3] Full rerun                      (~20 min)
echo    [4] Also build full report          (~10 sec)
echo    [0] Exit
echo ============================================================
set /p sel=Select:

if "%sel%"=="1" "%PY%" qc\run.py
if "%sel%"=="2" "%PY%" qc\run.py --locate
if "%sel%"=="3" "%PY%" qc\run.py --all
if "%sel%"=="4" "%PY%" qc\run.py --full-report
if "%sel%"=="0" exit /b

echo.
echo Done. Press any key to close.
pause >nul
exit /b

:probe
rem %~1 may be a command name ("python", "py -3.12") or a space-free exe path
%~1 -c "import docx" >nul 2>nul
if not errorlevel 1 set "PY=%~1"
exit /b
