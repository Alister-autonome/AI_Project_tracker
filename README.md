# 🚀 JobFiller: Autonome + Gadgets Hub + Application Tracker

[![Build macOS PKG Installer](https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler/actions/workflows/build-mac-pkg.yml/badge.svg)](https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler/actions/workflows/build-mac-pkg.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://apple.com/macos)
[![Powered by Claude Code](https://img.shields.io/badge/Engine-Claude%20Code%20CLI%20%2B%20Playwright%20MCP-purple.svg)](https://anthropic.com)
[![UI: Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io)

An open-source, local-first macOS job application automation suite and CRM tracker. **Autonome** uses Claude Code CLI and the Playwright MCP browser engine to navigate complex job forms, auto-fill your personal details and screening questions from your master profile, attach your resume, and **hold the browser tab open right before the final submission button** so you always stay in complete control.

Paired with a built-in **📊 CRM-style Application Tracker** and a modular **🧰 Gadgets Hub** (featuring PDF resume & tailored cover letter drafting, live Notion database synchronization, and automated Trello card creation).

---

## 🌟 Key Highlights & Philosophy

- 🛡️ **"Fill-and-Hold" Safety Guarantee**: Autonome will **never** click the final "Submit" button. It fills all form fields, uploads your resume, and keeps the Chrome tab open for your final visual review and approval.
- 🔒 **100% Local-First & Private**: No cloud backends, no middleman databases, zero telemetry. Your resume, profile answers, tokens, and job history live strictly on your Mac.
- 🔄 **Zero-Friction Boot-Time Auto-Updates**: Every time you launch `Job Filler.app`, it checks GitHub and pulls the latest features and Gadgets without touching or overwriting your personal files (`profile.md`, `resume.pdf`, `applications_history.csv`, `gadgets_config.json`, or Chrome cookies).
- 🧩 **Modular Gadgets**: Connect Notion, Trello, and automated PDF cover letters with one-click toggles in the local dashboard.

---

## 📥 Installation

1. Navigate to the [**Releases**](https://github.com/YOUR_GITHUB_USERNAME/mac-job-filler/releases/latest) page of this repository.
2. Download the latest **`JobFiller.pkg`** installer.
3. On your Mac, right-click `JobFiller.pkg` -> click **Open** (to bypass Gatekeeper for open-source unsigned packages) and follow the installer prompts.

The installer stages the application suite to `~/Desktop/JobFiller` and places a **`Job Filler.app`** shortcut directly onto your Desktop and inside `/Applications`.

---

## ⚡ 3-Step First-Time Setup

1. **Add Your Resume**:
   - Drop your `resume.pdf` into `~/Desktop/JobFiller/` (or upload it directly via the **PDF Gadget** inside the web dashboard).
2. **Launch the App**:
   - Double-click **`Job Filler.app`** on your Desktop. On first launch, the script automatically verifies and installs prerequisites (Homebrew, Node, Python, Claude Code CLI, Playwright MCP, and Streamlit in an isolated virtual environment).
3. **Authenticate Claude Code (Once Only)**:
   - If you haven't linked Claude yet, open a new Terminal window, run:
     ```bash
     claude
     ```
   - Type `/login` and authenticate with your Claude account (Pro/Team/Enterprise). That's it!

---

## 🖥️ Dashboard Overview (4 Core Tabs)

When `Job Filler.app` starts, it opens the local Streamlit dashboard at `http://localhost:8501`:

### 1. 🤖 Autonome (Batch Auto-Filler)
- Paste a queue of job URLs (Greenhouse, Lever, Workday, Taleo, Ashby, LinkedIn Jobs, etc.).
- Autonome launches a persistent Chromium instance via Playwright MCP.
- Claude analyzes the form, cross-references `profile.md`, uploads `resume.pdf`, and drafts bespoke answers for open questions.
- Automatically extracts the **Company Name** and **Role Title**, logs the application to your Tracker, triggers active Notion/Trello Gadgets, and leaves every application tab ready for you to review and submit.

### 2. 📊 Interactive Application Tracker
- **Top KPI Cards**: Real-time counters for *Total Tracked*, *Ready to Review*, *Applied*, *Interviewing*, and *Offers*.
- **Search & Filter**: Instantly search by company, role title, or notes, or filter by application status.
- **Editable Data Table**: Built with `st.data_editor` to update statuses (`Ready to Review`, `Applied`, `Assessment`, `Interviewing`, `Offer`, `Rejected`, `Archived`), edit salary, recruiter notes, and save modifications directly to `applications_history.csv`.
- **Batch Actions & Export**: One-click *"Mark All 'Ready' as 'Applied'"* button and direct CSV download.
- **Manual Application Logger**: Expander to log offline jobs, referrals, or direct outreach.

### 3. 🧰 Modular Gadgets Hub
- **📄 PDF Gadget**:
  - Upload or replace `resume.pdf` in-browser with live file-size inspection.
  - Enable automatic tailored cover letter generation during Autonome queue execution.
  - Standalone Cover Letter Generator: Paste any job description to generate an instant, targeted Markdown cover letter via Claude.
- **📓 Notion Gadget**:
  - Configure your Notion Integration Token (`secret_...` or `ntn_...`) and Database ID.
  - Automatically pushes every filled application as a new database row (storing Title, URL, and Status). Includes an interactive test button.
- **📋 Trello Gadget**:
  - Enter your Trello API Key, Token, and Target List ID.
  - Creates a new Trello card on your target board column for every job filled by Autonome. Includes an interactive test button.

### 4. 👤 Master Profile (`profile.md`)
- In-browser Markdown editor for your personal details, work authorization, salary expectations, employment history, and screening answer templates.
- Changes are saved directly to `profile.md` on your machine and are fully immune to Git updates.

---

## 🔄 How the Auto-Update System Works

Every time you click `Job Filler.app`, `launcher.sh` executes the following sequence:

```
[Double-click Job Filler.app]
            │
            ▼
┌───────────────────────────────────────────────┐
│  Check GitHub remote origin (main branch)    │
│  git fetch origin main                        │
└───────────────────────┬───────────────────────┘
                        │
          ┌─────────────┴─────────────┐
     Update found?               No update / Offline
          │                                   │
          ▼                                   ▼
┌──────────────────────────────┐    ┌───────────────────────────┐
│ git reset --hard origin/main │    │ Continue with local build │
└──────────────┬───────────────┘    └─────────────┬─────────────┘
               │                                  │
               └─────────────────┬────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────┐
│  Preserve Personal Files:                                     │
│  - profile.md (never overwritten)                            │
│  - resume.pdf & cover_letter.md                              │
│  - applications_history.csv                                   │
│  - gadgets_config.json                                        │
│  - chrome-profile/ (retains all active logins & cookies)      │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│  Verify & launch Streamlit app.py in virtual environment      │
└───────────────────────────────────────────────────────────────┘
```

You can also trigger a live update check anytime right from the dashboard sidebar using the **"🔄 Check & Pull GitHub Update"** button.

---

## 🏗️ Repository Structure

```
├── .github/
│   └── workflows/
│       └── build-mac-pkg.yml    # GitHub Actions macOS runner that compiles JobFiller.pkg
├── .gitattributes               # Enforces strict Unix LF line endings on Windows & macOS
├── .gitignore                   # Excludes personal profile, resume, keys, and CSV data
├── LICENSE                      # MIT Open Source License
├── README.md                    # Project documentation & user guide
├── profile.example.md           # Starter template for profile.md
├── app.py                       # Streamlit web UI (Autonome + Tracker + Gadgets)
└── launcher.sh                  # Self-updating bash bootstrapper for macOS
```

---

## ⚙️ Building the Native `.pkg` via GitHub Actions

This repository includes an automated workflow (`.github/workflows/build-mac-pkg.yml`) that triggers on every push to `main` and on manual dispatch:

1. Checks out the repository on a native `macos-latest` GitHub runner.
2. Injects the actual repository URL into `launcher.sh`.
3. Constructs the macOS bundle hierarchy (`/Applications/Job Filler.app`) with custom `Info.plist` and terminal launcher script.
4. Packages a `postinstall` script that initializes the user's `~/Desktop/JobFiller` workspace safely without overwriting existing profiles.
5. Runs Apple's native `pkgbuild` utility to compile `JobFiller.pkg`.
6. Publishes the compiled `.pkg` asset to GitHub Releases under the `latest` tag.

---

## 🤝 Contributing

Contributions are welcome! If you want to add new Gadgets (e.g. Google Sheets sync, Slack webhook alerts, LinkedIn job scraper integration), feel free to fork the repository, create a branch, and submit a pull request.

Please ensure all files maintain strict Unix LF line endings (`.gitattributes` is configured to handle this automatically).

---

## 📄 License

Distributed under the [MIT License](LICENSE). Free for personal and commercial use.
