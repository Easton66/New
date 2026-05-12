@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   MediaCfg Editor - Build Script
echo ========================================
echo.

REM Try common Python commands first
set PYCMD=
for %%c in (python py python3) do (
    %%c --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYCMD=%%c
        goto :found_python
    )
)

REM Search common install locations
echo Searching for Python...
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "%LOCALAPPDATA%\Programs\Python\Python38"
    "%PROGRAMFILES%\Python312"
    "%PROGRAMFILES%\Python311"
    "%PROGRAMFILES%\Python310"
    "%PROGRAMFILES%\Python39"
    "%PROGRAMFILES%\Python38"
    "C:\Python312"
    "C:\Python311"
    "C:\Python310"
) do (
    if exist %%d\python.exe (
        set PYCMD=%%d\python.exe
        echo [OK] Found: !PYCMD!
        goto :found_python
    )
)

echo [ERROR] Python not found.
echo.
echo Please install Python 3.8+ from:
echo   https://www.python.org/downloads/
echo.
echo IMPORTANT: Check "Add Python to PATH" during install!
echo.
pause
exit /b 1

:found_python
echo !PYCMD! --version
!PYCMD! --version
echo.

echo [1/2] Installing dependencies...
!PYCMD! -m pip install PySide6 pyinstaller -q
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Try running manually:
    echo   !PYCMD! -m pip install PySide6 pyinstaller
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [2/2] Building EXE (this may take 3-5 minutes)...
!PYCMD! -m PyInstaller MediaCfgEditor.spec
if !errorlevel! neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Build complete!
echo   EXE: dist\MediaCfgEditor.exe
echo ========================================
pause
