import streamlit as st
import subprocess
import shutil
import json
import os
import re
import io
import random
import urllib.request
import pandas as pd
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader
from docx import Document

IS_WINDOWS = os.name == "nt"
CLAUDE_BIN = "claude.cmd" if IS_WINDOWS else "claude"

# Default to Sonnet 5.5 alias to preserve user's Claude compute quota
SONNET_MODEL_OPTIONS = [
    "sonnet",
    "claude-sonnet-5-5",
    "claude-sonnet-4-5"
]

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_PATH = BASE_DIR / "profile.md"
EXAMPLE_PROFILE_PATH = BASE_DIR / "profile.example.md"
RESUME_PDF_PATH = BASE_DIR / "resume.pdf"
RESUME_DOCX_PATH = BASE_DIR / "resume.docx"
COVER_LETTER_PATH = BASE_DIR / "cover_letter.md"
GADGETS_CONFIG_PATH = BASE_DIR / "gadgets_config.json"
HISTORY_PATH = BASE_DIR / "applications_history.csv"

STATUS_OPTIONS = [
    "Ready to Review",
    "Applied",
    "Assessment",
    "Interviewing",
    "Offer",
    "Rejected",
    "Archived"
]

TRACKER_COLUMNS = ["Date", "Company", "Role", "Status", "URL", "Notes"]

FUN_QUOTES_AND_PUNS = [
    "💡 **Job Fact:** Roughly 70% of jobs are never published publicly—and for the other 30%, you now have a robot filling out the forms!",
    "😄 **Career Pun:** Why did the resume go to the gym? To get a little more *work experience*!",
    "🚀 **Motivational Boost:** Every 'No' or ghosted application is just one step closer to the company that says 'When can you start?'",
    "😄 **Career Pun:** I used to work at a calendar factory, but I got fired for taking a couple of days off. Let's find you a better gig today!",
    "💡 **Did You Know?** Tailoring your resume and answers increases interview callbacks by up to 2.4x—good thing Autonome reads your Master Profile every time!",
    "😄 **Career Pun:** Interviewer: 'Where do you see yourself in 5 years?' Me: 'Hopefully not still typing my work history into Workday after uploading my PDF!'",
    "🌟 **Motivational Boost:** You don't need 100 job offers—you only need **one** great 'Yes'. Let's queue up some links and go get it!",
    "😄 **Career Pun:** My friend got a job at the bakery because he really *kneaded* the dough. Let's go get yours!"
]

st.set_page_config(page_title="Autonome & Job Tracker Suite", layout="wide")

# Seed profile.md on first run if missing
if not PROFILE_PATH.exists() and EXAMPLE_PROFILE_PATH.exists():
    shutil.copy(EXAMPLE_PROFILE_PATH, PROFILE_PATH)

def get_active_resume_path():
    if RESUME_PDF_PATH.exists():
        return RESUME_PDF_PATH
    if RESUME_DOCX_PATH.exists():
        return RESUME_DOCX_PATH
    return None

def save_and_extract_resume(uploaded_file):
    """Saves uploaded .pdf or .docx locally and extracts its plain text."""
    raw_bytes = uploaded_file.read()
    ext = Path(uploaded_file.name).suffix.lower()
    extracted_text = ""

    if ext == ".pdf":
        RESUME_PDF_PATH.write_bytes(raw_bytes)
        try:
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            extracted_text = "\n".join(pages).strip()
        except Exception as e:
            extracted_text = f"[Could not extract PDF text automatically: {e}]"
    elif ext == ".docx":
        RESUME_DOCX_PATH.write_bytes(raw_bytes)
        try:
            doc = Document(io.BytesIO(raw_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            extracted_text = "\n".join(paragraphs).strip()
        except Exception as e:
            extracted_text = f"[Could not extract Word .docx text automatically: {e}]"

    return extracted_text

def load_tracker_df():
    if not HISTORY_PATH.exists():
        df = pd.DataFrame(columns=TRACKER_COLUMNS)
        df.to_csv(HISTORY_PATH, index=False)
        return df
    try:
        df = pd.read_csv(HISTORY_PATH, dtype=str).fillna("")
        if "timestamp" in df.columns and "Date" not in df.columns:
            df = df.rename(columns={"timestamp": "Date", "url": "URL", "status": "Status"})
        for col in TRACKER_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[TRACKER_COLUMNS]
    except Exception:
        return pd.DataFrame(columns=TRACKER_COLUMNS)

def save_tracker_df(df):
    df[TRACKER_COLUMNS].to_csv(HISTORY_PATH, index=False)

def append_application_to_tracker(company, role, status, url, notes=""):
    df = load_tracker_df()
    new_row = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Company": company or "Unknown Company",
        "Role": role or "Job Application",
        "Status": status,
        "URL": url,
        "Notes": notes
    }])
    df = pd.concat([new_row, df], ignore_index=True)
    save_tracker_df(df)

def load_gadgets_config():
    default_cfg = {
        "user_name": "",
        "onboarding_complete": False,
        "claude_model": "sonnet",
        "notion_enabled": False,
        "notion_token": "",
        "notion_database_id": "",
        "pdf_auto_cover_letter": False
    }
    if GADGETS_CONFIG_PATH.exists():
        try:
            saved = json.loads(GADGETS_CONFIG_PATH.read_text(encoding="utf-8"))
            default_cfg.update(saved)
        except Exception:
            pass
    return default_cfg

def save_gadgets_config(cfg):
    GADGETS_CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

def get_git_version():
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.stdout.strip() if res.returncode == 0 else "local"
    except Exception:
        return "local"

def push_to_notion(cfg, company, role, job_url, status_note="Ready to Review"):
    if not (cfg.get("notion_enabled") and cfg.get("notion_token") and cfg.get("notion_database_id")):
        return False, "Notion Gadget not configured or disabled."
    try:
        title_text = f"{company} — {role}" if company and company != "Unknown Company" else job_url
        payload = json.dumps({
            "parent": {"database_id": cfg["notion_database_id"]},
            "properties": {
                "Name": {"title": [{"text": {"content": title_text[:100]}}]},
                "URL": {"url": job_url},
                "Status": {"rich_text": [{"text": {"content": status_note}}]}
            }
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=payload,
            headers={
                "Authorization": f"Bearer {cfg['notion_token']}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201), "Synced to Notion database!"
    except Exception as e:
        return False, f"Notion error: {e}"

gadgets_cfg = load_gadgets_config()
tracker_df = load_tracker_df()
active_resume = get_active_resume_path()
active_model = gadgets_cfg.get("claude_model", "sonnet")

if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(FUN_QUOTES_AND_PUNS)

if "show_onboarding" not in st.session_state:
    st.session_state.show_onboarding = not gadgets_cfg.get("onboarding_complete", False)

# Sidebar: System Updates, Sonnet 5.5 Compute Saver, Onboarding Trigger & Stats
with st.sidebar:
    st.header("⚙️ Autonome Suite")
    os_badge = "🪟 Windows" if IS_WINDOWS else "🍎 macOS"
    st.caption(f"Platform: **{os_badge}** | Build: `{get_git_version()}`")
    st.success(f"⚡ **Compute Saver Active:** Locked to **Sonnet 5.5** (`{active_model}`)")

    with st.expander("🔧 Change Sonnet 5.5 Model ID"):
        selected_model = st.selectbox(
            "Sonnet 5.5 CLI Flag:",
            options=SONNET_MODEL_OPTIONS,
            index=SONNET_MODEL_OPTIONS.index(active_model) if active_model in SONNET_MODEL_OPTIONS else 0,
            help="Uses Sonnet 5.5 instead of Opus to conserve your Claude Pro compute quota."
        )
        if selected_model != active_model:
            gadgets_cfg["claude_model"] = selected_model
            save_gadgets_config(gadgets_cfg)
            st.rerun()

    if st.button("🔄 Check & Pull GitHub Update"):
        with st.spinner("Checking GitHub for updates..."):
            fetch = subprocess.run(["git", "fetch", "origin", "main"], cwd=str(BASE_DIR), capture_output=True, text=True)
            reset = subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=str(BASE_DIR), capture_output=True, text=True)
            if fetch.returncode == 0 and reset.returncode == 0:
                st.success("Updated to latest version! Reloading...")
                st.rerun()
            else:
                st.warning("Could not reach GitHub. Running current local version.")

    if st.button("✨ Re-run Onboarding Wizard"):
        st.session_state.show_onboarding = True
        st.rerun()

    st.divider()
    st.subheader("📊 Quick Tracker Stats")
    st.write(f"🗂️ **Total Tracked:** {len(tracker_df)}")
    st.write(f"⏳ **Ready to Review:** {len(tracker_df[tracker_df['Status'] == 'Ready to Review'])}")
    st.write(f"✅ **Applied:** {len(tracker_df[tracker_df['Status'] == 'Applied'])}")
    st.write(f"🎤 **Interviewing:** {len(tracker_df[tracker_df['Status'] == 'Interviewing'])}")

    st.divider()
    st.subheader("🧰 Active Gadgets")
    resume_label = f"✅ {active_resume.name}" if active_resume else "❌ Missing"
    st.write(f"📄 **Resume File:** {resume_label}")
    st.write(f"📝 **Auto Cover Letter:** {'🟢 ON' if gadgets_cfg.get('pdf_auto_cover_letter') else '⚪ OFF'}")
    st.write(f"📓 **Notion Sync:** {'🟢 ON' if gadgets_cfg.get('notion_enabled') else '⚪ OFF'}")

# =========================================================
# PERSONALIZED GREETING BANNER ("Hi [Name]!" + Pun / Fact)
# =========================================================
display_name = gadgets_cfg.get("user_name", "").strip() or "Friend"
greet_col1, greet_col2 = st.columns([5, 1])
with greet_col1:
    st.title(f"👋 Hi {display_name}! Ready to land your next role?")
    st.info(st.session_state.current_quote)
with greet_col2:
    st.write("")
    st.write("")
    if st.button("🎲 New Pun / Fact"):
        st.session_state.current_quote = random.choice(FUN_QUOTES_AND_PUNS)
        st.rerun()

# =========================================================
# INTERACTIVE FIRST-RUN ONBOARDING WIZARD
# =========================================================
if st.session_state.show_onboarding:
    with st.container(border=True):
        st.subheader("🎉 Welcome! Let's Set Up Your Profile & Resume (Takes 60 Seconds)")
        st.markdown(
            "Complete this quick setup so **Autonome** knows your name, has your **PDF or Word (`.docx`) resume**, "
            "and builds your `profile.md` answer sheet automatically using **Sonnet 5.5**."
        )

        ob_col1, ob_col2 = st.columns(2)
        with ob_col1:
            st.markdown("#### 1. Your Basic Details")
            ob_name = st.text_input("What's your first name (or preferred name)?", value=gadgets_cfg.get("user_name", ""), placeholder="e.g. Sarah")
            ob_full_name = st.text_input("Full Legal Name (for job forms)", value=ob_name, placeholder="e.g. Sarah Jenkins")
            ob_email = st.text_input("Email Address", placeholder="sarah@example.com")
            ob_phone = st.text_input("Phone Number", placeholder="555-123-4567")
            ob_location = st.text_input("City, State / Country", placeholder="Melbourne, VIC (or Austin, TX)")
            ob_linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...")

        with ob_col2:
            st.markdown("#### 2. Upload Your Resume (`.pdf` or `.docx`)")
            ob_resume = st.file_uploader(
                "Attach your PDF or Word Resume — we'll extract your experience automatically:",
                type=["pdf", "docx"],
                key="onboarding_resume_uploader"
            )
            extracted_resume_preview = st.session_state.get("extracted_resume_text", "")
            if ob_resume is not None:
                extracted_resume_preview = save_and_extract_resume(ob_resume)
                st.session_state.extracted_resume_text = extracted_resume_preview
                st.success(f"✅ Saved `{ob_resume.name}` and extracted {len(extracted_resume_preview)} characters of text!")

            st.markdown("#### 3. Standard Screening Preferences")
            ob_work_auth = st.selectbox("Authorized to work in target country?", ["Yes", "No"])
            ob_sponsorship = st.selectbox("Require Visa Sponsorship now or in the future?", ["No", "Yes"])
            ob_salary = st.text_input("Desired Salary Expectations", placeholder="e.g. $95,000 - $115,000")
            ob_notice = st.text_input("Earliest Start Date / Notice Period", value="2 weeks notice")

        if extracted_resume_preview:
            with st.expander("📄 Preview Extracted Resume Text", expanded=False):
                st.text_area("Extracted from your resume:", value=extracted_resume_preview, height=150)

        btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
        with btn_col1:
            if st.button("🚀 Save Profile & Finish Onboarding", type="primary"):
                chosen_name = ob_name.strip() or (ob_full_name.strip().split(" ")[0] if ob_full_name.strip() else "Friend")
                gadgets_cfg["user_name"] = chosen_name
                gadgets_cfg["onboarding_complete"] = True
                save_gadgets_config(gadgets_cfg)

                compiled_profile = f"""# Candidate Information
- Preferred Name: {chosen_name}
- Full Name: {ob_full_name.strip() or chosen_name}
- Email: {ob_email.strip()}
- Phone: {ob_phone.strip()}
- Location: {ob_location.strip()}
- LinkedIn: {ob_linkedin.strip()}

# Work Authorization & Demographics
- Authorized to work in the country of application: {ob_work_auth}
- Requires Visa Sponsorship now or in the future: {ob_sponsorship}
- Desired Salary Range: {ob_salary.strip()}
- Earliest Start Date / Notice Period: {ob_notice.strip()}
- Gender / Ethnicity / Veteran / Disability: Prefer not to say

# Extracted Resume Content & Work History
{extracted_resume_preview if extracted_resume_preview else "Paste your work history or upload a PDF/Word resume in the Gadgets tab."}

# Standard Screening Answers
- "Why do you want to work here?": Write a concise 2-3 sentence answer connecting my background and resume experience to the specific role description on the page.
"""
                PROFILE_PATH.write_text(compiled_profile, encoding="utf-8")
                st.session_state.show_onboarding = False
                st.success(f"Welcome aboard, {chosen_name}! Your Master Profile (`profile.md`) is ready.")
                st.rerun()

        with btn_col2:
            if st.button("🪄 Auto-Polish Profile with Sonnet 5.5"):
                if not extracted_resume_preview:
                    st.warning("Upload a PDF or Word resume first so Sonnet 5.5 can structure it!")
                else:
                    with st.spinner("Sonnet 5.5 is structuring your resume & answers into profile.md..."):
                        chosen_name = ob_name.strip() or "Friend"
                        gadgets_cfg["user_name"] = chosen_name
                        gadgets_cfg["onboarding_complete"] = True
                        save_gadgets_config(gadgets_cfg)
                        polish_prompt = (
                            f"Create a clean, comprehensive markdown file at {PROFILE_PATH} for job applications. "
                            f"Include Candidate Info (Name: {ob_full_name or chosen_name}, Email: {ob_email}, Phone: {ob_phone}, "
                            f"Location: {ob_location}, LinkedIn: {ob_linkedin}), Work Auth ({ob_work_auth}, Sponsorship: {ob_sponsorship}, "
                            f"Salary: {ob_salary}, Notice: {ob_notice}), and organize this raw resume text into clean Work History, "
                            f"Skills, and Education sections:\n\n{extracted_resume_preview}"
                        )
                        subprocess.run(
                            [
                                CLAUDE_BIN,
                                "--model", active_model,
                                "-p", polish_prompt,
                                "--allowedTools", "Read,Write"
                            ],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace"
                        )
                        st.session_state.show_onboarding = False
                        st.rerun()

        with btn_col3:
            if st.button("Skip for Now"):
                gadgets_cfg["onboarding_complete"] = True
                save_gadgets_config(gadgets_cfg)
                st.session_state.show_onboarding = False
                st.rerun()

# =========================================================
# MAIN 4-TAB INTERFACE (1:1 MAC & WINDOWS PARITY)
# =========================================================
tab_autonome, tab_tracker, tab_gadgets, tab_profile = st.tabs([
    "🤖 Autonome (Sonnet 5.5 Filler)",
    f"📊 Application Tracker ({len(tracker_df)})",
    "🧰 Gadgets Hub (PDF/Word · Notion)",
    "👤 Master Profile"
])

# ==========================================
# TAB 1: AUTONOME (SONNET 5.5 FILL & HOLD)
# ==========================================
with tab_autonome:
    st.subheader("🤖 Autonome: Batch Fill & Hold (Powered by Sonnet 5.5)")
    st.markdown(
        "Paste job links below. **Autonome** uses **Claude Sonnet 5.5** (`--model " + active_model + "`) to conserve your compute power while "
        "filling out forms in Chrome, uploading your `.pdf` or `.docx` resume, logging the Company & Role to your **Tracker**, and stopping before Submit."
    )

    urls_input = st.text_area(
        "Paste Job URLs (one per line):",
        height=180,
        placeholder="https://boards.greenhouse.io/...\nhttps://jobs.lever.co/..."
    )

    if st.button("▶️ Launch Autonome Queue (Sonnet 5.5)", type="primary"):
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
        if not urls:
            st.warning("Please paste at least one job URL.")
        else:
            resume_to_use = get_active_resume_path() or RESUME_PDF_PATH
            for i, url in enumerate(urls, 1):
                with st.status(f"({i}/{len(urls)}) Sonnet 5.5 processing: {url}", expanded=True) as status:
                    log_box = st.empty()
                    logs = ""

                    cover_letter_instruction = ""
                    if gadgets_cfg.get("pdf_auto_cover_letter"):
                        cover_letter_instruction = (
                            f"Also write a tailored 3-paragraph cover letter for this specific job to {COVER_LETTER_PATH} "
                            f"and paste or upload it if the form asks for a cover letter. "
                        )

                    prompt = (
                        f"Read {PROFILE_PATH}. Using the Playwright MCP browser, open a NEW tab and navigate to {url}. "
                        f"If there is an 'Apply' button, click it to reach the application form. "
                        f"Fill out all form fields accurately using {PROFILE_PATH} and upload the resume file from {resume_to_use}. "
                        f"{cover_letter_instruction}"
                        f"STRICT RULES: "
                        f"1. NEVER click the final 'Submit' button. "
                        f"2. NEVER close the browser or the tab—leave it open for human review. "
                        f"3. If a login wall or CAPTCHA appears, pause and state that human intervention is needed. "
                        f"4. At the very end of your response, output a single metadata line in this exact format: "
                        f"TRACKER_META: Company=<Company Name> | Role=<Job Title> | Notes=<1 short sentence on any fields needing review>"
                    )

                    process = subprocess.Popen(
                        [
                            CLAUDE_BIN,
                            "--model", active_model,
                            "-p", prompt,
                            "--allowedTools", "mcp__playwright__*,Read,Write"
                        ],
                        cwd=str(BASE_DIR),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace"
                    )

                    for line in process.stdout:
                        logs += line
                        log_box.code(logs, language="markdown")

                    process.wait()

                    detected_company = "Unknown Company"
                    detected_role = "Job Application"
                    detected_notes = "Filled by Autonome (Sonnet 5.5) — check open Chrome tab to submit."
                    meta_match = re.search(
                        r"TRACKER_META:\s*Company=([^|\n]+)\|\s*Role=([^|\n]+)\|\s*Notes=([^\n]+)",
                        logs
                    )
                    if meta_match:
                        detected_company = meta_match.group(1).strip()
                        detected_role = meta_match.group(2).strip()
                        detected_notes = meta_match.group(3).strip()

                    append_application_to_tracker(
                        company=detected_company,
                        role=detected_role,
                        status="Ready to Review",
                        url=url,
                        notes=detected_notes
                    )

                    if gadgets_cfg.get("notion_enabled"):
                        ok, msg = push_to_notion(gadgets_cfg, detected_company, detected_role, url, "Ready to Review")
                        st.caption(f"📓 Notion Gadget: {msg}")

                    status.update(label=f"✅ Logged & Ready in Chrome: {detected_company} — {detected_role}", state="complete")

# ==========================================
# TAB 2: INTERACTIVE APPLICATION TRACKER
# ==========================================
with tab_tracker:
    st.subheader("📊 Job Application Tracker")
    st.caption(
        "Every link processed by Autonome is automatically logged here. Once you review and click Submit in Chrome, "
        "change the status below from **Ready to Review** to **Applied**!"
    )

    df_current = load_tracker_df()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🗂️ Total Jobs", len(df_current))
    kpi2.metric("⏳ Ready to Review", len(df_current[df_current["Status"] == "Ready to Review"]))
    kpi3.metric("🚀 Applied", len(df_current[df_current["Status"] == "Applied"]))
    kpi4.metric("🎤 Interviewing", len(df_current[df_current["Status"] == "Interviewing"]))
    kpi5.metric("🏆 Offers", len(df_current[df_current["Status"] == "Offer"]))

    st.divider()

    with st.expander("➕ Log a Job Application Manually"):
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            manual_company = st.text_input("Company Name", placeholder="e.g. Stripe")
            manual_role = st.text_input("Role Title", placeholder="e.g. Product Marketing Manager")
        with m_col2:
            manual_status = st.selectbox("Initial Status", STATUS_OPTIONS, index=1)
            manual_url = st.text_input("Job Posting URL", placeholder="https://...")
        with m_col3:
            manual_notes = st.text_area("Notes / Next Steps", height=108, placeholder="Referral from Sam; follow up next Tuesday.")

        if st.button("💾 Add to Tracker"):
            if not manual_company.strip() and not manual_url.strip():
                st.warning("Please enter at least a Company Name or Job URL.")
            else:
                append_application_to_tracker(
                    company=manual_company.strip(),
                    role=manual_role.strip(),
                    status=manual_status,
                    url=manual_url.strip(),
                    notes=manual_notes.strip()
                )
                st.success("Added application to tracker!")
                st.rerun()

    f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Filter by Company, Role, or Notes:", placeholder="Type to search...")
    with f_col2:
        status_filter = st.multiselect("Filter by Status:", STATUS_OPTIONS, default=[])
    with f_col3:
        st.write("")
        st.write("")
        if st.button("✅ Mark All 'Ready' as 'Applied'"):
            df_current.loc[df_current["Status"] == "Ready to Review", "Status"] = "Applied"
            save_tracker_df(df_current)
            st.toast("Updated all Ready to Review items to Applied!")
            st.rerun()

    filtered_df = df_current.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        mask = (
            filtered_df["Company"].str.lower().str.contains(q, na=False) |
            filtered_df["Role"].str.lower().str.contains(q, na=False) |
            filtered_df["Notes"].str.lower().str.contains(q, na=False)
        )
        filtered_df = filtered_df[mask]
    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Date": st.column_config.TextColumn("Date Logged", width="small"),
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Role": st.column_config.TextColumn("Role Title", width="medium"),
            "Status": st.column_config.SelectboxColumn(
                "Application Status",
                options=STATUS_OPTIONS,
                required=True,
                width="medium"
            ),
            "URL": st.column_config.LinkColumn("Job Link", display_text="Open Job Page ↗", width="small"),
            "Notes": st.column_config.TextColumn("Notes / Checklist", width="large")
        },
        key="tracker_editor"
    )

    act_col1, act_col2, act_col3 = st.columns([1, 1, 2])
    with act_col1:
        if st.button("💾 Save Tracker Edits", type="primary"):
            if not search_query.strip() and not status_filter:
                save_tracker_df(edited_df)
            else:
                full_df = load_tracker_df()
                full_df.update(edited_df)
                save_tracker_df(full_df)
            st.success("Tracker changes saved!")
            st.rerun()
    with act_col2:
        st.download_button(
            "⬇️ Export Tracker CSV",
            data=HISTORY_PATH.read_bytes() if HISTORY_PATH.exists() else b"",
            file_name=f"job_applications_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ==========================================
# TAB 3: DEDICATED GADGETS HUB (PDF/WORD + NOTION)
# ==========================================
with tab_gadgets:
    st.subheader("🧰 Modular Gadgets Hub")
    st.caption("Configure and run your standalone or integrated Gadgets for PDF/Word Resumes and Notion.")

    g_col1, g_col2 = st.columns(2)

    with g_col1:
        with st.container(border=True):
            st.markdown("### 📄 PDF & Word Resume Gadget")
            st.caption("Manage `.pdf` or `.docx` resumes, extract text into `profile.md`, and generate cover letters with Sonnet 5.5.")

            if RESUME_PDF_PATH.exists():
                size_kb = round(RESUME_PDF_PATH.stat().st_size / 1024, 1)
                st.success(f"Active PDF: `resume.pdf` ({size_kb} KB)")
            if RESUME_DOCX_PATH.exists():
                size_kb = round(RESUME_DOCX_PATH.stat().st_size / 1024, 1)
                st.success(f"Active Word Doc: `resume.docx` ({size_kb} KB)")
            if not RESUME_PDF_PATH.exists() and not RESUME_DOCX_PATH.exists():
                st.error("No `resume.pdf` or `resume.docx` found yet.")

            uploaded_doc = st.file_uploader("Upload or Replace Resume (`.pdf` or `.docx`)", type=["pdf", "docx"])
            if uploaded_doc is not None:
                extracted_text = save_and_extract_resume(uploaded_doc)
                st.success(f"✅ Saved `{uploaded_doc.name}` ({len(extracted_text)} chars extracted)!")
                if st.button("📥 Append Extracted Resume Text to Master Profile"):
                    current_prof = PROFILE_PATH.read_text(encoding="utf-8") if PROFILE_PATH.exists() else ""
                    PROFILE_PATH.write_text(current_prof + "\n\n# Imported Resume Text\n" + extracted_text, encoding="utf-8")
                    st.toast("Appended resume text into profile.md!")

            auto_cl = st.checkbox(
                "Auto-generate tailored Cover Letter during Autonome runs",
                value=gadgets_cfg.get("pdf_auto_cover_letter", False)
            )
            if auto_cl != gadgets_cfg.get("pdf_auto_cover_letter"):
                gadgets_cfg["pdf_auto_cover_letter"] = auto_cl
                save_gadgets_config(gadgets_cfg)
                st.toast("Updated Resume Gadget preference!")

            st.divider()
            st.markdown("**Quick Cover Letter Generator (Sonnet 5.5)**")
            jd_snippet = st.text_area("Paste Job Description or URL:", height=100, key="pdf_jd")
            if st.button("✨ Generate Cover Letter"):
                if not jd_snippet.strip():
                    st.warning("Paste a job description or link first.")
                else:
                    with st.spinner("Sonnet 5.5 is drafting your tailored cover letter..."):
                        cl_prompt = (
                            f"Read {PROFILE_PATH}. Draft a concise, high-impact cover letter tailored to this job: {jd_snippet}. "
                            f"Save the output to {COVER_LETTER_PATH} and print it."
                        )
                        res = subprocess.run(
                            [
                                CLAUDE_BIN,
                                "--model", active_model,
                                "-p", cl_prompt,
                                "--allowedTools", "Read,Write"
                            ],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace"
                        )
                        st.code(res.stdout, language="markdown")

    with g_col2:
        with st.container(border=True):
            st.markdown("### 📓 Notion Gadget")
            st.caption("Auto-log filled applications to your Notion Database.")

            notion_enabled = st.toggle("Enable Notion Sync", value=gadgets_cfg.get("notion_enabled", False))
            notion_token = st.text_input(
                "Notion Integration Token (`ntn_...` or `secret_...`)",
                value=gadgets_cfg.get("notion_token", ""),
                type="password"
            )
            notion_db = st.text_input(
                "Notion Database ID",
                value=gadgets_cfg.get("notion_database_id", ""),
                help="Ensure your Notion database has 'Name' (Title), 'URL' (URL), and 'Status' (Text) properties."
            )

            if st.button("💾 Save Notion Gadget"):
                gadgets_cfg["notion_enabled"] = notion_enabled
                gadgets_cfg["notion_token"] = notion_token.strip()
                gadgets_cfg["notion_database_id"] = notion_db.strip()
                save_gadgets_config(gadgets_cfg)
                st.success("Notion Gadget settings saved!")

            if st.button("🧪 Test Notion Connection"):
                ok, msg = push_to_notion(
                    {
                        "notion_enabled": True,
                        "notion_token": notion_token.strip(),
                        "notion_database_id": notion_db.strip()
                    },
                    "Acme Corp",
                    "Sample Role",
                    "https://example.com/test-job",
                    "Gadget Connection Test"
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# ==========================================
# TAB 4: MASTER PROFILE EDITOR
# ==========================================
with tab_profile:
    st.subheader("👤 Your Master Profile (`profile.md`)")
    st.caption("Autonome and the PDF/Word Gadget read this file to answer application questions accurately.")
    col_p1, col_p2 = st.columns([3, 1])
    with col_p2:
        new_pref_name = st.text_input("Your Greeting Name:", value=gadgets_cfg.get("user_name", ""))
        if st.button("💬 Update Greeting Name"):
            gadgets_cfg["user_name"] = new_pref_name.strip()
            save_gadgets_config(gadgets_cfg)
            st.toast("Greeting name updated!")
            st.rerun()

    profile_text = PROFILE_PATH.read_text(encoding="utf-8") if PROFILE_PATH.exists() else ""
    updated_profile = st.text_area("Edit your details & standard answers:", value=profile_text, height=450)
    if st.button("💾 Save Master Profile"):
        PROFILE_PATH.write_text(updated_profile, encoding="utf-8")
        st.toast("Profile saved! (Protected from Git updates)")
