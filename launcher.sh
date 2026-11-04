#!/bin/bash
TARGET_DIR="$HOME/Desktop/JobFiller"
REPO_URL="https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler.git"

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.npm-global/bin:$PATH"

echo "=========================================="
echo "   Autonome & Gadgets — Checking Updates  "
echo "=========================================="

# 1. Self-Update from GitHub on Boot (Preserves untracked profile.md, resume.pdf, applications_history.csv & gadgets_config.json)
if command -v git &> /dev/null; then
    if [ ! -d ".git" ]; then
        git init -q
        git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    fi
    if git fetch origin main --quiet 2>/dev/null; then
        LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "none")
        REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null || echo "none")
        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ "$REMOTE_HASH" != "none" ]; then
            echo "⬇️  New update found on GitHub! Updating Autonome & Gadgets..."
            git reset --hard origin/main --quiet
            chmod +x "$TARGET_DIR/launcher.sh"
            echo "✅ Updated to latest version ($REMOTE_HASH)."
        else
            echo "✅ Already running the latest version."
        fi
    else
        echo "⚠️  Offline or unable to reach GitHub. Running current local version."
    fi
fi

# 2. Seed profile.md from template without overwriting user edits
if [ ! -f "profile.md" ] && [ -f "profile.example.md" ]; then
    cp profile.example.md profile.md
fi

# 3. Install dependencies if missing
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew (you may be prompted for your Mac password)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
fi

if ! command -v node &> /dev/null || ! command -v python3 &> /dev/null; then
    echo "Installing Node.js and Python..."
    brew install node python
fi

if ! command -v claude &> /dev/null; then
    echo "Installing Claude Code CLI..."
    npm install -g @anthropic-ai/claude-code
fi

if ! claude mcp list 2>/dev/null | grep -q "playwright"; then
    echo "Configuring Playwright Chrome Browser Bridge..."
    claude mcp add playwright -s user -- npx -y @playwright/mcp@latest --browser chrome --user-data-dir "$TARGET_DIR/chrome-profile"
fi

if [ ! -d "venv" ]; then
    echo "Creating local Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip streamlit pandas pypdf
else
    source venv/bin/activate
    pip install -q pandas pypdf
fi

echo ""
echo "💡 FIRST TIME TIP: If applications fail to start, open a new Terminal tab,"
echo "   type 'claude', and then type '/login' once to link your Claude Pro account."
echo ""

streamlit run app.py
