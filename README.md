# 🚀 JobFiller: Autonome + Onboarding + PDF/Word Resume Reader + Notion & Application Tracker

[![Build Mac (.pkg) & Windows (.exe) Installers](https://github.com/Alister-autonome/AI_Project_tracker/actions/workflows/build-installers.yml/badge.svg)](https://github.com/Alister-autonome/AI_Project_tracker/actions/workflows/build-installers.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS & Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/Alister-autonome/AI_Project_tracker)
[![Compute Saver: Sonnet 5.5 Locked](https://img.shields.io/badge/Compute%20Saver-Sonnet%205.5%20Locked-green.svg)](https://anthropic.com)
[![Engine: Claude Code CLI + Playwright](https://img.shields.io/badge/Engine-Claude%20Code%20CLI%20%2B%20Playwright%20MCP-purple.svg)](https://anthropic.com)
[![UI: Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io)

An open-source, local-first **cross-platform (macOS & Windows)** job application automation suite and CRM tracker with complete 1:1 feature parity. **Autonome** uses Claude Code CLI locked to **Sonnet 5.5** and the Playwright MCP browser engine to navigate complex job forms, auto-fill your personal details and screening questions from your master profile, attach your **PDF or Word (`.docx`)** resume, and **hold the browser tab open right before the final submission button** so you always stay in complete control.

Paired with an **Interactive First-Run Onboarding Wizard**, a **Personalized Greeting Banner**, a built-in **📊 CRM-style Application Tracker**, and a modular **🧰 Gadgets Hub** (featuring PDF/Word resume text extraction & Sonnet 5.5 cover letter drafting and live Notion database sync).

---

## 🌟 Key Highlights & Philosophy

- ⚡ **Compute-Saving Sonnet 5.5 Lock:** Every Claude Code CLI invocation is locked to **Sonnet 5.5** (`sonnet` / `claude-sonnet-5-5`), preventing accidental exhaustion of heavy Opus compute quotas during batch runs.
- 🪟🍎 **1:1 Cross-Platform Parity:** Both macOS (`JobFiller.pkg`) and Windows (`JobFiller-Setup.exe`) share the exact same UI, launchers, dependencies (`streamlit`, `pandas`, `pypdf`, `python-docx`), and boot-time auto-updaters.
- 🎉 **Interactive First-Run Onboarding:** Quick 60-second wizard greets you by name, extracts experience from your uploaded **`.pdf` or `.docx`** resume into `profile.md`, and can automatically structure your master answers using Sonnet 5.5.
- 👋 **Personalized Greeting Banner:** Welcomes you by name (`"👋 Hi [Name]!"`) on every launch with a randomized motivational fact, career quote, or job-hunting pun (with a "🎲 New Pun / Fact" button).
- 🛡️ **"Fill-and-Hold" Safety Guarantee:** Autonome **never** clicks the final "Submit" button. It fills all form fields, uploads your resume, and leaves the Chrome tab open for your visual inspection.
- 🔒 **100% Local-First & Private:** All personal files (`profile.md`, `resume.pdf`, `resume.docx`, `cover_letter.md`, `applications_history.csv`, `gadgets_config.json`, and browser cookies) remain strictly local and are never tracked or overwritten by Git updates.

---

## 📥 Installation

Navigate to the [**Releases**](https://github.com/Alister-autonome/AI_Project_tracker/releases/latest) page of this repository and download the installer for your OS:

### 🍎 For macOS Users (`JobFiller.pkg`)
1. Download `JobFiller.pkg`.
2. Right-click `JobFiller.pkg` -> click **Open** (to bypass Gatekeeper for open-source unsigned packages).
3. Walk through the native installer. A shortcut will be placed on your Desktop (`Job Filler.app`) and in `/Applications`.

### 🪟 For Windows Users (`JobFiller-Setup.exe`)
1. Download `JobFiller-Setup.exe`.
2. Double-click to run the setup wizard.
3. It installs to `Desktop\JobFiller` and places an **Autonome Job Filler** shortcut on your Desktop and Start Menu.

---

## ⚡ 3-Step First-Time Setup

1. **Launch the App**:
   - On macOS: Double-click `Job Filler.app` on your Desktop.
   - On Windows: Double-click `Autonome Job Filler` on your Desktop (or run `launcher.bat`).
2. **Complete the 60-Second Onboarding Wizard**:
   - Enter your name.
   - Drop your **PDF (`.pdf`)** or **Word (`.docx`)** resume to extract text into your profile automatically.
   - Choose whether to auto-polish your profile with Sonnet 5.5.
3. **Authenticate Claude Code (Once Only)**:
   - If you haven't linked Claude yet, open a Terminal (macOS) or Command Prompt (Windows):
     ```bash
     claude
     ```
   - Type `/login` and authenticate with your Claude account (Pro/Team/Enterprise). That's it!

---

## 🖥️ Dashboard Overview (4 Core Tabs)

### 1. 🤖 Autonome (Sonnet 5.5 Filler)
- Paste a batch of job URLs (Greenhouse, Lever, Workday, Taleo, Ashby, LinkedIn, etc.).
- Autonome launches a persistent Chromium instance via Playwright MCP.
- Claude Sonnet 5.5 fills the fields using your profile and attaches `resume.pdf` or `resume.docx`.
- Automatically extracts the **Company Name** and **Role Title**, pushes to your Tracker (and Notion if enabled), and leaves the browser tab open right before Submit.

### 2. 📊 Interactive Application Tracker
- **Top KPI Cards**: Real-time counters for *Total Tracked*, *Ready to Review*, *Applied*, *Interviewing*, and *Offers*.
- **Search & Filter**: Instantly search by company, role title, or notes, or filter by application status.
- **Editable Data Table**: Built with `st.data_editor` to update statuses (`Ready to Review`, `Applied`, `Assessment`, `Interviewing`, `Offer`, `Rejected`, `Archived`), edit notes, and save modifications back to `applications_history.csv`.
- **Batch Actions & Export**: One-click *"Mark All 'Ready' as 'Applied'"* button and direct CSV download.
- **Manual Application Logger**: Expander to log offline jobs, referrals, or direct outreach.

### 3. 🧰 Modular Gadgets Hub (PDF/Word & Notion)
- **📄 PDF & Word Resume Gadget**:
  - Upload or replace `.pdf` or `.docx` resumes with live file size and text extraction previews.
  - Option to append extracted resume text directly to `profile.md`.
  - Auto-generate tailored cover letters during batch runs.
  - Standalone Cover Letter Generator: Paste any job description to generate an instant, targeted Markdown cover letter via Sonnet 5.5.
- **📓 Notion Gadget**:
  - Configure your Notion Integration Token (`ntn_...` or `secret_...`) and Database ID.
  - Automatically pushes every filled application as a new database row (storing Title, URL, and Status). Includes an interactive test button.

### 4. 👤 Master Profile (`profile.md`)
- In-browser editor for your personal details, work authorization, salary expectations, employment history, and screening answer templates.
- Update your personalized greeting name anytime.

---

## 🔄 How the Auto-Update System Works

Every time you click `Job Filler.app` (macOS) or `Autonome Job Filler` (Windows):

1. The launcher checks your GitHub repository `main` branch.
2. If an update is detected, it pulls the new code via `git reset --hard origin/main`.
3. **Preserves Personal Files:** Your `profile.md`, `resume.pdf`, `resume.docx`, `cover_letter.md`, `applications_history.csv`, `gadgets_config.json`, and Chrome session cookies are never touched or overwritten.
4. Activates the local `venv` with all dependencies (`streamlit`, `pandas`, `pypdf`, `python-docx`) and launches `app.py`.

---

## 🏗️ Repository Structure

```
├── .github/
│   └── workflows/
│       └── build-installers.yml # Dual-platform GitHub Actions (builds .pkg and .exe)
├── .gitattributes               # LF for scripts/python/markdown, CRLF for .bat and .iss
├── .gitignore                   # Excludes personal profile, resume (.pdf/.docx), keys, CSV
├── LICENSE                      # MIT Open Source License
├── README.md                    # Documentation & user guide
├── profile.example.md           # Starter template for profile.md
├── app.py                       # 1:1 cross-platform Streamlit UI (Sonnet 5.5 locked)
├── launcher.bat                 # Windows auto-updating launcher (CRLF)
├── launcher.sh                  # macOS auto-updating launcher (LF)
└── installer.iss                # Inno Setup script for JobFiller-Setup.exe (CRLF)
```

---

## ⚙️ Building Installers via GitHub Actions

This repository includes `.github/workflows/build-installers.yml` which triggers on every push to `main`:

1. **`build-mac-pkg`** (`macos-latest`): Injects repo URL, stages payload, bundles `Job Filler.app`, and runs Apple's native `pkgbuild` to output `JobFiller.pkg`.
2. **`build-windows-exe`** (`windows-latest`): Injects repo URL, compiles `installer.iss` using Inno Setup compiler, and outputs `JobFiller-Setup.exe`.
3. **`release`** (`ubuntu-latest`): Downloads both artifacts and publishes them together to the **`latest`** GitHub Release.

---

## 🤝 Contributing

Contributions are welcome! If you want to add new Gadgets or improve form-filling heuristics, fork the repo and open a pull request.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Free for personal and commercial use.
