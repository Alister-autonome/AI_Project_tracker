# 🎯 Job Hunter

[![Build installers](https://github.com/Alister-autonome/AI_Project_tracker/actions/workflows/build-installers.yml/badge.svg)](https://github.com/Alister-autonome/AI_Project_tracker/actions/workflows/build-installers.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Your own job-search assistant, powered by **your Claude account**, running **only on your computer** (macOS or Windows).

- 📊 **Tracker:** every job in one place, with statuses, contacts, follow-up reminders and a pipeline summary.
- 🤖 **Auto-Apply:** paste job links. Claude fills each application in Chrome from your profile, uploads your resume, then **stops before Submit** so you check and send it yourself.
- ✉️ **Cover letters & LinkedIn messages:** written in your voice, using only what's true in your profile.
- 💬 **Ask Claude:** a job-search coach that knows your background (screening questions, fit checks, interview prep).
- 📈 **Usage:** your real Claude plan limits (5-hour and weekly) plus every request Job Hunter has made.

---

## What you need

- A **Claude Pro or Max** plan ([claude.ai](https://claude.ai)).
- **Google Chrome** (only for Auto-Apply).
- About 5 minutes the first time.

## Install (guided)

1. Go to [**Releases**](https://github.com/Alister-autonome/AI_Project_tracker/releases/latest) and download:
   - **Mac:** `JobFiller.pkg`. Right-click → **Open** (it isn't from the App Store, so macOS asks once).
   - **Windows:** `JobFiller-Setup.exe`. If SmartScreen appears, click **More info → Run anyway**.
2. Open **Job Hunter** from your Desktop. A setup window appears and does the rest:
   - installs Python, Node.js and Claude Code if they're missing,
   - asks you to **sign in to Claude once** (your browser opens, sign in, come back),
   - opens Job Hunter in your browser at `http://localhost:8501`.
3. In the app, follow **Welcome → Step 1 / Step 2**:
   - Step 1 shows a checklist (Claude installed, signed in, Chrome, Node.js) with a one-click fix for anything missing.
   - Step 2 takes your name and contact details and your resume (PDF or Word).
4. Open the **👤 Profile** tab and fill in *Positioning*, *Proof links* and **Don't claim**, so Claude never says you've used a tool you haven't.

Next time, just open Job Hunter from your Desktop. It updates itself automatically.

## Using it

| Tab | What to do |
|---|---|
| 📊 Tracker | Add jobs, change Status as you go, set a Follow-up date. Edits save automatically. |
| 🤖 Auto-Apply | Paste links → **Start**. Check each Chrome tab, finish anything listed, press Submit yourself, then mark it *Applied*. |
| ✉️ Cover Letter & Outreach | Paste the job ad → cover letter (download as Word), LinkedIn connection note + message, or a fit check. |
| 💬 Ask Claude | Anything job-search related. Click **New conversation** to start fresh. |
| 📈 Usage | Plan limits and history. **Check now** in the sidebar refreshes the limits. |

**Tips that work:** apply within 48 hours of a job being posted, send the hiring manager a short note the same day, and follow up after a week.

---

## Privacy & security

- **Local only.** The app listens on `127.0.0.1`, so other devices on your Wi-Fi can't open it. Usage statistics are off.
- **Your files stay in the app folder** (`profile.md`, resume, tracker, usage log). They're excluded from Git, so updates never overwrite them.
- **Claude can't run commands on your computer.** Every request uses Claude Code's `--restricted` mode, with no shell, code or file tools, no MCP servers, and no personal settings or plugins loaded.
- **Auto-Apply gets a browser and nothing else.** It uses its own Chrome profile (`chrome-profile/`), with Playwright's "run code" tool blocked. It's told to treat web pages as untrusted, never press Enter in forms, never tick consent boxes, never submit, and to stop at logins and CAPTCHAs.
- **Job ads are treated as data.** Pasted text is wrapped and marked as third-party content, so instructions hidden in an ad are ignored.
- **Lean on your plan.** Requests skip Claude Code's default context, so a cover letter costs a few thousand tokens instead of 100k+.
- **Updates come only from this repository** (`main` branch), and the launcher checks for them each time it starts.

## For developers

```
app.py                  Streamlit app (all UI + Claude CLI bridge)
.streamlit/config.toml  localhost-only server + theme
launcher.sh / .bat      installs prerequisites, signs in to Claude, auto-updates, launches
installer.iss           Windows installer (Inno Setup)
.github/workflows/      builds JobFiller.pkg + JobFiller-Setup.exe on every push to main
profile.example.md      starter profile
```

Run from source: `pip install streamlit pandas pypdf python-docx`, then `streamlit run app.py` (needs `claude` signed in).

MIT licensed.
