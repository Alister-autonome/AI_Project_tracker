#!/bin/bash
TARGET_DIR="$HOME/Desktop/JobFiller"
REPO_URL="https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler.git"

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR" || exit 1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$HOME/.npm-global/bin:$PATH"

echo "=========================================="
echo "   Job Hunter -- Checking for updates"
echo "=========================================="

if command -v git &> /dev/null; then
    if [ ! -d ".git" ]; then
        git init -q
        git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    fi
    if git fetch origin main --quiet 2>/dev/null; then
        LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "none")
        REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null || echo "none")
        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ "$REMOTE_HASH" != "none" ]; then
            echo "⬇️  New update found on GitHub! Updating Autonome..."
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

if [ ! -f "profile.md" ] && [ -f "profile.example.md" ]; then
    cp profile.example.md profile.md
fi

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
    echo "Installing Claude Code..."
    curl -fsSL https://claude.ai/install.sh | bash || npm install -g @anthropic-ai/claude-code
    export PATH="$HOME/.local/bin:$PATH"
fi

if ! claude auth status 2>/dev/null | grep -q '"loggedIn": true'; then
    echo ""
    echo "=========================================="
    echo " 🔑 One-time step: connect your Claude account"
    echo " A browser window will open. Sign in with your Claude Pro or Max account,"
    echo " then come back here."
    echo "=========================================="
    claude auth login
fi

if [ ! -d "venv" ]; then
    echo "Creating local Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip streamlit pandas pypdf python-docx
else
    source venv/bin/activate
    pip install -q streamlit pandas pypdf python-docx
fi

echo ""
echo "Opening Job Hunter at http://localhost:8501 (only this computer can see it)"
streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
