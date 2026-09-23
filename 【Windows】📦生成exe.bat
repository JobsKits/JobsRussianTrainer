@echo off
rem Jobs Russian Trainer: build a standalone EXE in project dist.
rem Missing dependencies are installed into the project .venv only.
setlocal
echo Jobs Russian Trainer - Windows EXE builder
echo Creates project .venv / build / dist. Installs missing dependencies online.
echo Log: %%TEMP%%\JobsRussianTrainer-build.log
echo Press Ctrl+C to cancel, or any key to continue.
pause >nul
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 -c "import sys, venv; assert sys.version_info.major == 3 and 11 <= sys.version_info.minor < 15" >nul 2>nul
if errorlevel 1 goto use_python
py -3 "%~dp0JobsRussianTrainer\scripts\manage.py" build --yes
goto done
:use_python
python -c "import sys, venv; assert sys.version_info.major == 3 and 11 <= sys.version_info.minor < 15" >nul 2>nul
if errorlevel 1 goto missing
python "%~dp0JobsRussianTrainer\scripts\manage.py" build --yes
goto done
:missing
echo Python 3.11-3.14 is required. Install from python.org and enable PATH.
pause
exit /b 1
:done
set "BUILD_RESULT=%ERRORLEVEL%"
if not "%BUILD_RESULT%"=="0" echo Build failed. Read the log in TEMP.
if "%BUILD_RESULT%"=="0" echo Build complete. Open the dist folder.
pause
exit /b %BUILD_RESULT%
