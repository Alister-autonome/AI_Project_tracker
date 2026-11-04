import streamlit as st
import subprocess
import shutil
import json
import re
import urllib.request
import urllib.parse
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_PATH = BASE_DIR / "profile.md"
EXAMPLE_PROFILE_PATH = BASE_DIR / "profile.example.md"
RESUME_PATH = BASE_DIR / "resume.pdf"
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

st.set_page_config(page_title="Autonome & Job Tracker Suite", layout="wide")

# Seed profile.md on first run if missing
if not PROFILE_PATH.exists() and EXAMPLE_PROFILE_PATH.exists():
    shutil.copy(EXAMPLE_PROFILE_PATH, PROFILE_PATH)

def load_tracker_df():
    if not HISTORY_PATH.exists():
        df = pd.DataFrame(columns=TRACKER_COLUMNS)
        df.to_csv(HISTORY_PATH, index=False)
        return df
    try:
        df = pd.read_csv(HISTORY_PATH, dtype=str).fillna("")
        # Migrate legacy 3-column CSVs gracefully if needed
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
        "notion_enabled": False,
        "notion_token": "",
        "notion_database_id": "",
        "trello_enabled": False,
        "trello_api_key": "",
        "trello_token": "",
        "trello_list_id": "",
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

def push_to_trello(cfg, company, role, job_url, status_note="Ready to Review"):
    if not (cfg.get("trello_enabled") and cfg.get("trello_api_key") and cfg.get("trello_token") and cfg.get("trello_list_id")):
        return False, "Trello Gadget not configured or disabled."
    try:
        card_title = f"{company} — {role}" if company and company != "Unknown Company" else f"Application: {job_url[:50]}"
        params = urllib.parse.urlencode({
            "idList": cfg["trello_list_id"],
            "key": cfg["trello_api_key"],
            "token": cfg["trello_token"],
            "name": card_title,
            "desc": f"Company: {company}\nRole: {role}\nStatus: {status_note}\nURL: {job_url}\nLogged: {datetime.now().isoformat()}"
        }).encode("utf-8")
        req = urllib.request.Request("https://api.trello.com/1/cards", data=params, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200, "Synced to Trello board!"
    except Exception as e:
        return False, f"Trello error: {e}"

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

# Sidebar: System Updates, Mini Pipeline Summary & Active Gadgets
with st.sidebar:
    st.header("⚙️ Autonome Suite")
    st.caption(f"Current Build: `{get_git_version()}`")
    if st.button("🔄 Check & Pull GitHub Update"):
        with st.spinner("Checking GitHub for updates..."):
            fetch = subprocess.run(["git", "fetch", "origin", "main"], cwd=str(BASE_DIR), capture_output=True, text=True)
            reset = subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=str(BASE_DIR), capture_output=True, text=True)
            if fetch.returncode == 0 and reset.returncode == 0:
                st.success("Updated to latest version! Reloading...")
                st.rerun()
            else:
                st.warning("Could not reach GitHub. Running current local version.")

    st.divider()
    st.subheader("📊 Quick Tracker Stats")
    st.write(f"🗂️ **Total Tracked:** {len(tracker_df)}")
    st.write(f"⏳ **Ready to Review:** {len(tracker_df[tracker_df['Status'] == 'Ready to Review'])}")
    st.write(f"✅ **Applied:** {len(tracker_df[tracker_df['Status'] == 'Applied'])}")
    st.write(f"🎤 **Interviewing:** {len(tracker_df[tracker_df['Status'] == 'Interviewing'])}")

    st.divider()
    st.subheader("🧰 Active Gadgets")
    st.write(f"📄 **PDF Resume:** {'✅ Ready' if RESUME_PATH.exists() else '❌ Missing'}")
    st.write(f"📝 **Auto Cover Letter:** {'🟢 ON' if gadgets_cfg.get('pdf_auto_cover_letter') else '⚪ OFF'}")
    st.write(f"📓 **Notion Sync:** {'🟢 ON' if gadgets_cfg.get('notion_enabled') else '⚪ OFF'}")
    st.write(f"📋 **Trello Sync:** {'🟢 ON' if gadgets_cfg.get('trello_enabled') else '⚪ OFF'}")

    st.divider()
    st.caption("💡 All personal files (`profile.md`, `resume.pdf`, `applications_history.csv`, and Gadget keys) are isolated from Git auto-updates.")

st.title("🚀 Autonome & Job Application Tracker")

tab_autonome, tab_tracker, tab_gadgets, tab_profile = st.tabs([
    "🤖 Autonome (Auto-Filler)",
    f"📊 Application Tracker ({len(tracker_df)})",
    "🧰 Gadgets Hub (PDF · Notion · Trello)",
    "👤 Master Profile"
])

# ==========================================
# TAB 1: AUTONOME (CORE FILL & HOLD ENGINE)
# ==========================================
with tab_autonome:
    st.subheader("🤖 Autonome: Batch Fill & Hold")
    st.markdown(
        "Paste job links below. **Autonome** will launch your persistent Chrome browser, fill out the fields using your Master Profile & PDF Gadget, "
        "automatically log the Company and Role to your **Application Tracker**, and leave every tab open right before the final Submit button."
    )

    urls_input = st.text_area(
        "Paste Job URLs (one per line):",
        height=180,
        placeholder="https://boards.greenhouse.io/...\nhttps://jobs.lever.co/..."
    )

    if st.button("▶️ Launch Autonome Queue", type="primary"):
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
        if not urls:
            st.warning("Please paste at least one job URL.")
        else:
            for i, url in enumerate(urls, 1):
                with st.status(f"({i}/{len(urls)}) Autonome processing: {url}", expanded=True) as status:
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
                        f"Fill out all form fields accurately using {PROFILE_PATH} and upload the resume from {RESUME_PATH}. "
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
                            "claude", "-p", prompt,
                            "--allowedTools", "mcp__playwright__*,Read,Write"
                        ],
                        cwd=str(BASE_DIR),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True
                    )

                    for line in process.stdout:
                        logs += line
                        log_box.code(logs, language="markdown")

                    process.wait()

                    # Parse extracted Company, Role, and Notes from Claude's output
                    detected_company = "Unknown Company"
                    detected_role = "Job Application"
                    detected_notes = "Filled by Autonome — check open Chrome tab to submit."
                    meta_match = re.search(
                        r"TRACKER_META:\s*Company=([^|\n]+)\|\s*Role=([^|\n]+)\|\s*Notes=([^\n]+)",
                        logs
                    )
                    if meta_match:
                        detected_company = meta_match.group(1).strip()
                        detected_role = meta_match.group(2).strip()
                        detected_notes = meta_match.group(3).strip()

                    # Save to local Application Tracker
                    append_application_to_tracker(
                        company=detected_company,
                        role=detected_role,
                        status="Ready to Review",
                        url=url,
                        notes=detected_notes
                    )

                    # Trigger enabled Gadgets automatically
                    if gadgets_cfg.get("trello_enabled"):
                        ok, msg = push_to_trello(gadgets_cfg, detected_company, detected_role, url, "Ready to Review")
                        st.caption(f"📋 Trello Gadget: {msg}")
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

    # Top KPI Dashboard Row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🗂️ Total Jobs", len(df_current))
    kpi2.metric("⏳ Ready to Review", len(df_current[df_current["Status"] == "Ready to Review"]))
    kpi3.metric("🚀 Applied", len(df_current[df_current["Status"] == "Applied"]))
    kpi4.metric("🎤 Interviewing", len(df_current[df_current["Status"] == "Interviewing"]))
    kpi5.metric("🏆 Offers", len(df_current[df_current["Status"] == "Offer"]))

    st.divider()

    # Add Manual Entry Expander
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

    # Search and Filter Controls
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

    # Apply view filters
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

    # Interactive Editable Table
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
                # Merge edits back into full dataframe by matching URL + Date
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
# TAB 3: DEDICATED GADGETS HUB
# ==========================================
with tab_gadgets:
    st.subheader("🧰 Modular Gadgets Hub")
    st.caption("Configure and run your standalone or integrated Gadgets for PDFs, Notion, and Trello.")

    g_col1, g_col2, g_col3 = st.columns(3)

    # --- PDF GADGET ---
    with g_col1:
        with st.container(border=True):
            st.markdown("### 📄 PDF Gadget")
            st.caption("Manage `resume.pdf` and tailored cover letters.")

            if RESUME_PATH.exists():
                size_kb = round(RESUME_PATH.stat().st_size / 1024, 1)
                st.success(f"Active `resume.pdf` ({size_kb} KB)")
            else:
                st.error("No `resume.pdf` found yet.")

            uploaded_pdf = st.file_uploader("Upload or Replace `resume.pdf`", type=["pdf"])
            if uploaded_pdf is not None:
                RESUME_PATH.write_bytes(uploaded_pdf.read())
                st.success("✅ Saved new `resume.pdf`!")
                st.rerun()

            auto_cl = st.checkbox(
                "Auto-generate tailored Cover Letter during Autonome runs",
                value=gadgets_cfg.get("pdf_auto_cover_letter", False)
            )
            if auto_cl != gadgets_cfg.get("pdf_auto_cover_letter"):
                gadgets_cfg["pdf_auto_cover_letter"] = auto_cl
                save_gadgets_config(gadgets_cfg)
                st.toast("Updated PDF Gadget preference!")

            st.divider()
            st.markdown("**Quick Cover Letter Generator**")
            jd_snippet = st.text_area("Paste Job Description or URL:", height=100, key="pdf_jd")
            if st.button("✨ Generate Cover Letter"):
                if not jd_snippet.strip():
                    st.warning("Paste a job description or link first.")
                else:
                    with st.spinner("Claude is drafting your tailored cover letter..."):
                        cl_prompt = (
                            f"Read {PROFILE_PATH}. Draft a concise, high-impact cover letter tailored to this job: {jd_snippet}. "
                            f"Save the output to {COVER_LETTER_PATH} and print it."
                        )
                        res = subprocess.run(
                            ["claude", "-p", cl_prompt, "--allowedTools", "Read,Write"],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True
                        )
                        st.code(res.stdout, language="markdown")

    # --- NOTION GADGET ---
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

    # --- TRELLO GADGET ---
    with g_col3:
        with st.container(border=True):
            st.markdown("### 📋 Trello Gadget")
            st.caption("Auto-create Trello cards for every filled job link.")

            trello_enabled = st.toggle("Enable Trello Sync", value=gadgets_cfg.get("trello_enabled", False))
            trello_key = st.text_input(
                "Trello API Key",
                value=gadgets_cfg.get("trello_api_key", ""),
                type="password"
            )
            trello_token = st.text_input(
                "Trello Token",
                value=gadgets_cfg.get("trello_token", ""),
                type="password"
            )
            trello_list = st.text_input(
                "Trello Target List ID",
                value=gadgets_cfg.get("trello_list_id", ""),
                help="Cards will be added to this column whenever Autonome prepares an application."
            )

            if st.button("💾 Save Trello Gadget"):
                gadgets_cfg["trello_enabled"] = trello_enabled
                gadgets_cfg["trello_api_key"] = trello_key.strip()
                gadgets_cfg["trello_token"] = trello_token.strip()
                gadgets_cfg["trello_list_id"] = trello_list.strip()
                save_gadgets_config(gadgets_cfg)
                st.success("Trello Gadget settings saved!")

            if st.button("🧪 Test Trello Connection"):
                ok, msg = push_to_trello(
                    {
                        "trello_enabled": True,
                        "trello_api_key": trello_key.strip(),
                        "trello_token": trello_token.strip(),
                        "trello_list_id": trello_list.strip()
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
    st.caption("Autonome and the PDF Gadget read this file to answer application questions accurately.")
    profile_text = PROFILE_PATH.read_text(encoding="utf-8") if PROFILE_PATH.exists() else ""
    updated_profile = st.text_area("Edit your details & standard answers:", value=profile_text, height=450)
    if st.button("💾 Save Master Profile"):
        PROFILE_PATH.write_text(updated_profile, encoding="utf-8")
        st.toast("Profile saved! (Protected from Git updates)")
