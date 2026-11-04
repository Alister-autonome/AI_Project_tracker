@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title Autonome Job Filler (Windows)

cd /d "%~dp0"
set "TARGET_DIR=%CD%"
set "REPO_URL=https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler.git"

:: Add standard Windows install locations to PATH immediately
set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%LOCALAPPDATA%\Python\pythoncore-3.14-64;C:\Program Files\Python312;C:\Program Files\Python312\Scripts;C:\Program Files\nodejs;%APPDATA%\npm;%PATH%"

echo ==========================================
echo    Autonome Job Filler -- Checking Updates
echo ==========================================

:: 1. Self-Update from GitHub on Boot (Preserves untracked personal files)
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if not exist ".git" (
        git init -q
        git remote add origin "%REPO_URL%" 2>nul || git remote set-url origin "%REPO_URL%"
    )
    git fetch origin main --quiet 2>nul
    if !ERRORLEVEL! EQU 0 (
        for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL_HASH=%%i
        for /f %%i in ('git rev-parse origin/main 2^>nul') do set REMOTE_HASH=%%i
        if not "!LOCAL_HASH!"=="!REMOTE_HASH!" (
            echo [Update] New version found on GitHub! Updating code...
            git reset --hard origin/main --quiet
            echo [OK] Updated to latest version.
        ) else (
            echo [OK] Already running the latest version.
        )
    ) else (
        echo [Info] Offline or repo not reachable yet. Running local version.
    )
)

:: 2. Seed profile.md from template without overwriting user edits
if not exist "profile.md" (
    if exist "profile.example.md" copy /Y "profile.example.md" "profile.md" >nul
)

:: 3. Check for Node.js on Windows
node -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Setup] Installing Node.js LTS via winget...
    winget install --id OpenJS.NodeJS.LTS -e --silent --accept-package-agreements --accept-source-agreements
    set "PATH=C:\Program Files\nodejs;%APPDATA%\npm;%PATH%"
)

:: 4. Check for REAL Python (Bypasses Windows 11 Microsoft Store fake python.exe stub)
set "PYTHON_CMD="
py -3 -c "import sys" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
) else (
    py -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_CMD=py"
    ) else (
        python -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PYTHON_CMD=python"
        )
    )
)

if "!PYTHON_CMD!"=="" (
    echo [Setup] Real Python 3 not found. Installing Python 3.12 via winget...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;C:\Program Files\Python312;C:\Program Files\Python312\Scripts;%PATH%"
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_CMD=""%LOCALAPPDATA%\Programs\Python\Python312\python.exe"""
    ) else if exist "C:\Program Files\Python312\python.exe" (
        set "PYTHON_CMD=""C:\Program Files\Python312\python.exe"""
    ) else (
        set "PYTHON_CMD=python"
    )
)

:: 5. Install Claude Code CLI if missing
call claude --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Setup] Installing Claude Code CLI...
    call npm install -g @anthropic-ai/claude-code
)

:: 6. Register Playwright MCP on Windows (using cmd /c npx wrapper required on Windows)
call claude mcp list 2>nul | findstr /I "playwright" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [Setup] Configuring Playwright Chrome Browser Bridge for Windows...
    call claude mcp add playwright -s user -- cmd /c npx -y @playwright/mcp@latest --browser chrome --user-data-dir "%TARGET_DIR%\chrome-profile"
)

:: 7. Build Python venv using real Python binary and launch Streamlit directly from venv
if not exist "venv\Scripts\python.exe" (
    echo [Setup] Creating local Python virtual environment...
    !PYTHON_CMD! -m venv venv
)

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Could not create Python virtual environment.
    echo Please close this window, open a fresh terminal, or install Python 3.12 from python.org.
    pause
    exit /b 1
)

echo [Setup] Verifying Python packages (streamlit, pandas, pypdf, python-docx)...
"%TARGET_DIR%\venv\Scripts\python.exe" -m pip install -q --upgrade pip streamlit pandas pypdf python-docx

echo.
echo [FIRST TIME TIP] If applications fail to start, open a new Command Prompt,
echo type 'claude', and then type '/login' once to link your Claude Pro account.
echo.

"%TARGET_DIR%\venv\Scripts\python.exe" -m streamlit run app.py
pause
