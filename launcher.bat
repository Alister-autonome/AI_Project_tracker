@echo off
setlocal EnableDelayedExpansion
title Autonome & Gadgets Suite (Windows)

cd /d "%~dp0"
set "TARGET_DIR=%CD%"
set "REPO_URL=https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler.git"

echo ==========================================
echo    Autonome ^& Gadgets — Checking Updates
echo ==========================================

:: 1. Self-Update from GitHub on Boot (Preserves untracked profile.md, resume.pdf/.docx, applications_history.csv & gadgets_config.json)
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

:: 3. Check for Node.js and Python on Windows (Install via winget if missing)
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Node.js via winget...
    winget install --id OpenJS.NodeJS.LTS -e --silent
    set "PATH=%PATH%;C:\Program Files\nodejs;%APPDATA%\npm"
)

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Python 3 via winget...
    winget install --id Python.Python.3.12 -e --silent
)

:: 4. Install Claude Code CLI if missing
where claude >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Claude Code CLI...
    call npm install -g @anthropic-ai/claude-code
)

:: 5. Register Playwright MCP on Windows (using cmd /c npx wrapper required on Windows)
call claude mcp list 2>nul | findstr /I "playwright" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Configuring Playwright Chrome Browser Bridge for Windows...
    call claude mcp add playwright -s user -- cmd /c npx -y @playwright/mcp@latest --browser chrome --user-data-dir "%TARGET_DIR%\chrome-profile"
)

:: 6. Set up Python venv with 1:1 PDF & Word (.docx) support and launch Streamlit
if not exist "venv\Scripts\activate.bat" (
    echo Creating local Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip streamlit pandas pypdf python-docx
) else (
    call venv\Scripts\activate.bat
    python -m pip install -q streamlit pandas pypdf python-docx
)

echo.
echo [FIRST TIME TIP] If applications fail to start, open a new Command Prompt,
echo type 'claude', and then type '/login' once to link your Claude Pro account.
echo.

streamlit run app.py
pause
