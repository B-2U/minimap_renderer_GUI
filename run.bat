@echo off

if not defined PYTHON (set PYTHON=python)
if not defined VENV_DIR (set VENV_DIR=renderer_venv)


if %ERRORLEVEL% == 0 goto :start_venv
echo Couldn't launch python
goto :show_stdout_stderr

:start_venv
if [%VENV_DIR%] == [-] goto :skip_venv
dir %VENV_DIR%\Scripts\Python.exe
if %ERRORLEVEL% == 0 goto :activate_venv

for /f "delims=" %%i in ('CALL %PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME="%%i"
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv %VENV_DIR%
if %ERRORLEVEL% == 0 goto :activate_venv
echo Unable to create venv in directory %VENV_DIR%
goto :show_stdout_stderr

:activate_venv

set PYTHON="%VENV_DIR%\Scripts\Python.exe"
call "%VENV_DIR%\Scripts\activate.bat"
echo venv %PYTHON%
goto :launch

:launch
%PYTHON% app.py %*
pause
exit /b