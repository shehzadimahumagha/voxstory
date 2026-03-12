"""
VoxStory — app.py

Streamlit UI: 5 modes + GitHub integration for code-aware artifact generation.
Run with: streamlit run app.py
"""

import json
import os
import uuid
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from agent.chain import (
    run_transcript_mode,
    run_refinement_mode,
    run_technical_mode,
    run_solution_mapping,
    run_synthesis,
)
from agent.github_tools import (
    validate_and_connect,
    get_repo_tree,
    get_file_content,
    get_repo_issues,
    build_context_block,
)
from exporters.docx_exporter import markdown_to_docx
from exporters.json_exporter import to_json_bytes

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="VoxStory",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background-color: #F4F5F7; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0747A6 0%, #172B4D 100%);
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
    section[data-testid="stSidebar"] hr { border-color: #1a4080 !important; }
    section[data-testid="stSidebar"] .stTextInput input {
        background: #0d3d8a !important;
        border: 1px solid #1a4080 !important;
        border-radius: 4px !important;
        color: #E2E8F0 !important;
        font-size: 0.82rem !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #4C9AFF !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect > div {
        background: #0d3d8a !important;
        border-color: #1a4080 !important;
    }
    section[data-testid="stSidebar"] .stCheckbox label { font-size: 0.82rem !important; }

    /* ── Logo ── */
    .vs-logo {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F1F5F9;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    .vs-logo-accent { color: #4C9AFF; }
    .vs-sub {
        font-size: 0.66rem;
        color: #6C8EAD;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 2px;
        margin-bottom: 1.2rem;
    }

    /* ── GitHub status badge ── */
    .gh-badge-on {
        display: inline-flex; align-items: center; gap: 6px;
        background: #003d1a; border: 1px solid #005c26;
        border-radius: 20px; padding: 3px 10px;
        font-size: 0.7rem; font-weight: 600;
        color: #4ADE80 !important;
    }
    .gh-badge-off {
        display: inline-flex; align-items: center; gap: 6px;
        background: #0d1829; border: 1px solid #1a2d4a;
        border-radius: 20px; padding: 3px 10px;
        font-size: 0.7rem; font-weight: 500;
        color: #6C8EAD !important;
    }
    .gh-dot-on {
        width: 7px; height: 7px; border-radius: 50%;
        background: #4ADE80; display: inline-block; flex-shrink: 0;
    }
    .gh-dot-off {
        width: 7px; height: 7px; border-radius: 50%;
        background: #4A6A8A; display: inline-block; flex-shrink: 0;
    }
    .gh-section-label {
        font-size: 0.66rem; font-weight: 700;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: #6C8EAD !important; margin-bottom: 6px;
    }

    /* ── Main page header ── */
    .main-header {
        padding: 1.5rem 0 1.25rem 0;
        border-bottom: 1px solid #DFE1E6;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 1.65rem; font-weight: 800;
        color: #172B4D; letter-spacing: -0.04em; margin: 0;
    }
    .main-title-accent { color: #0052CC; }
    .main-subtitle {
        font-size: 0.875rem; color: #5E6C84;
        margin: 5px 0 0 0; font-weight: 400;
    }

    /* ── GitHub context ribbon ── */
    .ctx-ribbon {
        background: #DEEBFF; border: 1px solid #B3D4FF;
        border-radius: 6px; padding: 9px 14px;
        font-size: 0.8rem; color: #0052CC !important;
        font-weight: 500; margin-bottom: 1.25rem;
        display: flex; align-items: center; gap: 8px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px; background: transparent;
        border-bottom: 2px solid #DFE1E6; padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; border: none !important;
        border-bottom: 2px solid transparent !important; margin-bottom: -2px;
        color: #5E6C84 !important; font-weight: 500 !important;
        font-size: 0.875rem !important; padding: 9px 18px !important;
        transition: color 0.12s;
    }
    .stTabs [aria-selected="true"] {
        color: #172B4D !important;
        border-bottom: 2px solid #0052CC !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #172B4D !important; }

    /* ── Section labels ── */
    .sec-label {
        font-size: 0.68rem; font-weight: 700;
        letter-spacing: 0.1em; text-transform: uppercase;
        color: #5E6C84; margin-bottom: 6px;
    }

    /* ── Mode badge ── */
    .mode-badge {
        display: inline-block; background: #DEEBFF;
        color: #0747A6; border: 1px solid #B3D4FF;
        border-radius: 3px; font-size: 0.67rem; font-weight: 700;
        letter-spacing: 0.08em; text-transform: uppercase;
        padding: 2px 8px; margin-bottom: 10px;
    }

    /* ── Input card ── */
    .stTextArea textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important; line-height: 1.65 !important;
        border: 1px solid #DFE1E6 !important; border-radius: 6px !important;
        background: #FAFBFC !important; color: #172B4D !important;
        resize: vertical;
    }
    .stTextArea textarea:focus {
        border-color: #0052CC !important;
        box-shadow: 0 0 0 3px rgba(0,82,204,0.1) !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: #0052CC !important; color: #FFF !important;
        border: none !important; border-radius: 4px !important;
        font-weight: 600 !important; font-size: 0.875rem !important;
        padding: 0.6rem 1.5rem !important; transition: background 0.15s !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button[kind="primary"]:hover { background: #0065FF !important; }
    .stButton > button[kind="primary"]:disabled {
        background: #DFE1E6 !important; color: #A5ADBA !important;
    }
    .stButton > button[kind="secondary"] {
        background: #F4F5F7 !important; color: #172B4D !important;
        border: 1px solid #DFE1E6 !important; border-radius: 4px !important;
        font-weight: 500 !important; font-size: 0.8rem !important;
        transition: all 0.12s !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #0052CC !important; color: #0052CC !important;
        background: #DEEBFF !important;
    }
    .stDownloadButton > button {
        background: #FFFFFF !important; color: #172B4D !important;
        border: 1px solid #DFE1E6 !important; border-radius: 4px !important;
        font-size: 0.84rem !important; font-weight: 500 !important;
        padding: 0.5rem 1rem !important; transition: all 0.12s !important;
    }
    .stDownloadButton > button:hover {
        border-color: #0052CC !important; color: #0052CC !important;
    }

    /* ── Output panel ── */
    .success-banner {
        background: #E3FCEF; border: 1px solid #ABF5D1;
        border-radius: 6px; padding: 10px 14px;
        font-size: 0.84rem; color: #00875A; font-weight: 500;
        margin-bottom: 1.25rem;
    }
    .output-empty {
        color: #5E6C84; font-size: 0.84rem; margin-bottom: 1rem;
    }
    .cap-item {
        font-size: 0.82rem; color: #5E6C84;
        padding: 6px 0; border-bottom: 1px solid #EBECF0;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #0052CC !important; }

    /* ── Role badges (Collaboration Board) ── */
    .role-badge {
        display: inline-block;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: 1px solid transparent;
        vertical-align: middle;
    }
    .role-badge-client    { background: #E3FAFC; color: #0C8599; border-color: #99E9F2; }
    .role-badge-ba        { background: #F3D9FA; color: #7948D9; border-color: #D0BFFF; }
    .role-badge-pm        { background: #FFF4E6; color: #E67700; border-color: #FFD8A8; }
    .role-badge-techlead  { background: #EBFBEE; color: #2F9E44; border-color: #B2F2BB; }
    .role-badge-dev       { background: #E7F5FF; color: #1971C2; border-color: #A5D8FF; }
    .role-badge-architect { background: #EDF2FF; color: #3B5BDB; border-color: #BAC8FF; }
    .role-badge-other     { background: #F4F5F7; color: #5E6C84; border-color: #DFE1E6; }

    /* ── Collaboration session header ── */
    .collab-session-header {
        background: #FFFFFF;
        border: 1px solid #DFE1E6;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .collab-session-name {
        font-size: 1rem;
        font-weight: 700;
        color: #172B4D;
    }
    .collab-session-meta {
        font-size: 0.75rem;
        color: #5E6C84;
        margin-left: auto;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Role CSS map ───────────────────────────────────────────────────────────────

ROLE_CSS_MAP = {
    "Client": "role-badge-client",
    "Business Analyst": "role-badge-ba",
    "Product Manager": "role-badge-pm",
    "Tech Lead": "role-badge-techlead",
    "Developer": "role-badge-dev",
    "Architect": "role-badge-architect",
    "Other": "role-badge-other",
}

ROLES = [
    "Client",
    "Business Analyst",
    "Product Manager",
    "Tech Lead",
    "Developer",
    "Architect",
    "Other",
]

# ── Helpers ────────────────────────────────────────────────────────────────────


def get_github_context() -> str:
    """Assembles the GitHub context block from session state."""
    if not st.session_state.get("gh_connected"):
        return ""
    repo_info = st.session_state.get("gh_repo_info", {})
    selected = st.session_state.get("gh_selected_files", [])
    cache = st.session_state.get("gh_file_contents", {})
    include_issues = st.session_state.get("gh_include_issues", False)
    files = [(p, cache[p]) for p in selected if p in cache]
    issues = st.session_state.get("gh_issues", []) if include_issues else []
    return build_context_block(repo_info, files, issues)


def _format_contributions(contributions: list) -> str:
    """Formats contribution dicts into the synthesis prompt input string."""
    lines = []
    for i, c in enumerate(contributions, 1):
        lines.append(f"### Contribution {i}")
        lines.append(f"**Name:** {c['name']}")
        lines.append(f"**Role:** {c['role']}")
        lines.append(f"**Perspective:**")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def _load_session_from_upload(uploaded_file):
    """Parse and validate an uploaded session JSON file. Returns dict or None."""
    try:
        data = json.loads(uploaded_file.read())
        required = {"session_id", "session_name", "created_at", "contributions"}
        if not required.issubset(data.keys()):
            st.error(
                "Invalid session file — missing required fields: "
                + ", ".join(sorted(required - set(data.keys())))
            )
            return None
        if "synthesis_result" not in data:
            data["synthesis_result"] = None
        return data
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON file: {exc}")
        return None
    except Exception as exc:
        st.error(f"Failed to load session: {exc}")
        return None


# ── API key resolution (env → UI input) ───────────────────────────────────────

_env_groq_key = os.getenv("GROQ_API_KEY", "")

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    # ── Logo ──
    st.markdown(
        '<div class="vs-logo">Vox<span class="vs-logo-accent">Story</span></div>'
        '<div class="vs-sub">AI BA &amp; Architect Agent</div>',
        unsafe_allow_html=True,
    )

    # ── Groq API key (shown when key not already in env) ──
    if not _env_groq_key:
        st.markdown(
            '<div class="gh-section-label">Groq API Key</div>',
            unsafe_allow_html=True,
        )
        ui_groq_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_xxxxxxxxxxxxxxxxxxxx",
            label_visibility="collapsed",
            help="Get a free key at console.groq.com — no credit card required.",
            key="ui_groq_key",
        )
        if ui_groq_key.strip():
            os.environ["GROQ_API_KEY"] = ui_groq_key.strip()
            st.markdown(
                '<div style="font-size:0.72rem;color:#4ADE80;margin-bottom:4px;">'
                'Key set — ready to generate.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.72rem;color:#6C8EAD;margin-bottom:2px;">'
                'Free key: <a href="https://console.groq.com" target="_blank" '
                'style="color:#4C9AFF;">console.groq.com</a></div>',
                unsafe_allow_html=True,
            )
        st.divider()

    # ── GitHub status ──
    if st.session_state.get("gh_connected"):
        repo_name = st.session_state.get("gh_repo_info", {}).get("name", "")
        st.markdown(
            f'<div class="gh-badge-on">'
            f'<span class="gh-dot-on"></span>&nbsp;{repo_name}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="gh-badge-off">'
            '<span class="gh-dot-off"></span>&nbsp;Not connected'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── GitHub Integration panel ──
    st.markdown(
        '<div class="gh-section-label">GitHub Integration</div>',
        unsafe_allow_html=True,
    )

    env_token = os.getenv("GITHUB_TOKEN", "")
    gh_token = st.text_input(
        "Token",
        value=env_token if env_token else "",
        type="password",
        placeholder="ghp_xxxxxxxxxxxx",
        label_visibility="collapsed",
        help="Fine-grained PAT with Contents + Issues read access.",
        key="gh_token_input",
    )

    gh_repo = st.text_input(
        "Repo",
        placeholder="owner/repo",
        label_visibility="collapsed",
        key="gh_repo_input",
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        connect_btn = st.button(
            "Connect", use_container_width=True, key="gh_connect", type="secondary"
        )
    with btn_col2:
        if st.session_state.get("gh_connected"):
            if st.button(
                "Disconnect",
                use_container_width=True,
                key="gh_disconnect",
                type="secondary",
            ):
                for k in [
                    "gh_connected", "gh_repo_info", "gh_repo_path",
                    "gh_tree", "gh_selected_files", "gh_file_contents",
                    "gh_issues", "gh_include_issues",
                ]:
                    st.session_state.pop(k, None)
                st.rerun()

    if connect_btn:
        if not gh_repo.strip():
            st.warning("Enter a repo path (owner/repo).")
        else:
            if gh_token.strip():
                os.environ["GITHUB_TOKEN"] = gh_token.strip()
            with st.spinner("Connecting..."):
                info = validate_and_connect(gh_repo.strip())
            if info["valid"]:
                st.session_state["gh_connected"] = True
                st.session_state["gh_repo_info"] = info
                st.session_state["gh_repo_path"] = gh_repo.strip()
                st.session_state["gh_file_contents"] = {}
                st.session_state["gh_selected_files"] = []
                with st.spinner("Loading file tree..."):
                    try:
                        st.session_state["gh_tree"] = get_repo_tree(gh_repo.strip())
                    except Exception as e:
                        st.session_state["gh_tree"] = []
                        st.warning(f"File tree unavailable: {e}")
                st.rerun()
            else:
                st.error(info.get("error", "Connection failed."))

    # ── File browser + issue toggle (only when connected) ──
    if st.session_state.get("gh_connected") and st.session_state.get("gh_tree"):
        tree = st.session_state["gh_tree"]
        file_paths = [i["path"] for i in tree if i["type"] == "file"]

        st.markdown(
            "<div style='height:6px'></div>"
            '<div class="gh-section-label" style="margin-top:8px">Context Files</div>',
            unsafe_allow_html=True,
        )

        selected_files = st.multiselect(
            "Files",
            options=file_paths,
            default=st.session_state.get("gh_selected_files", []),
            label_visibility="collapsed",
            key="gh_file_selector",
        )
        st.session_state["gh_selected_files"] = selected_files

        if selected_files:
            if st.button(
                "Load Files into Context",
                use_container_width=True,
                key="gh_load",
                type="secondary",
            ):
                repo_path = st.session_state["gh_repo_path"]
                cache = st.session_state.get("gh_file_contents", {})
                with st.spinner("Loading..."):
                    for path in selected_files:
                        if path not in cache:
                            try:
                                cache[path] = get_file_content(repo_path, path)
                            except Exception as e:
                                cache[path] = f"[Error: {e}]"
                st.session_state["gh_file_contents"] = cache
                st.success(f"{len(selected_files)} file(s) loaded into context")

        include_issues = st.checkbox(
            "Include open issues",
            value=st.session_state.get("gh_include_issues", False),
            key="gh_issues_cb",
        )
        st.session_state["gh_include_issues"] = include_issues

        if include_issues:
            issues = st.session_state.get("gh_issues")
            if not issues:
                try:
                    issues = get_repo_issues(st.session_state["gh_repo_path"])
                    st.session_state["gh_issues"] = issues
                except Exception as e:
                    st.warning(f"Issues unavailable: {e}")
            if issues:
                st.caption(f"{len(issues)} open issues loaded")

    st.divider()

    # ── Methodology ──
    st.markdown(
        '<div class="gh-section-label">Methodology</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.78rem;color:#6C8EAD;line-height:1.75;margin-top:4px;'>"
        "INVEST criteria · Gherkin AC<br>"
        "Business language enforcement<br>"
        "Technical stories + API contracts<br>"
        "Solution architecture mapping<br>"
        "Multi-stakeholder synthesis<br>"
        "GitHub-aware code context<br>"
        "Jira-compatible JSON export"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Main page header ───────────────────────────────────────────────────────────

st.markdown(
    '<div class="main-header">'
    '<p class="main-title">Vox<span class="main-title-accent">Story</span></p>'
    '<p class="main-subtitle">'
    "AI Business Analyst &amp; Solutions Architect — "
    "from raw requirements to Jira-ready artifacts and architecture maps."
    "</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── GitHub context ribbon ──────────────────────────────────────────────────────

if st.session_state.get("gh_connected"):
    repo_name = st.session_state.get("gh_repo_info", {}).get("name", "")
    loaded_files = list(st.session_state.get("gh_file_contents", {}).keys())
    issues_count = (
        len(st.session_state.get("gh_issues", []))
        if st.session_state.get("gh_include_issues")
        else 0
    )
    parts = [f"<strong>{repo_name}</strong>"]
    if loaded_files:
        parts.append(f"{len(loaded_files)} file(s) in context")
    if issues_count:
        parts.append(f"{issues_count} issues in context")
    if not loaded_files and not issues_count:
        parts.append("repo metadata only — select files for deeper context")
    st.markdown(
        f'<div class="ctx-ribbon">GitHub: {" · ".join(parts)}</div>',
        unsafe_allow_html=True,
    )

# ── Setup banner (no API key) ──────────────────────────────────────────────────

if not os.getenv("GROQ_API_KEY"):
    st.markdown(
        """
<div style="background:#FFF7E6;border:1px solid #FFD8A8;border-radius:6px;
            padding:14px 18px;margin-bottom:1.25rem;display:flex;
            align-items:flex-start;gap:12px;">
  <div style="flex:1;">
    <div style="font-size:0.88rem;font-weight:700;color:#E67700;margin-bottom:4px;">
      Setup Required — Enter your Groq API Key to get started
    </div>
    <div style="font-size:0.82rem;color:#7E5E00;line-height:1.6;">
      VoxStory runs on Groq's ultra-fast inference (completely free).
      Enter your key in the sidebar — no credit card needed.<br>
      Get one in under 60 seconds at
      <a href="https://console.groq.com" target="_blank"
         style="color:#0052CC;font-weight:600;">console.groq.com</a>
      &nbsp;&rarr;&nbsp; Create API Key.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ── Mode tabs ──────────────────────────────────────────────────────────────────

tab_transcript, tab_refine, tab_technical, tab_solution, tab_collab = st.tabs(
    [
        "Transcript Mode",
        "Refinement Mode",
        "Technical Story Mode",
        "Solution Map",
        "Collaboration Board",
    ]
)

# ── Shared renderer ────────────────────────────────────────────────────────────

_CAPABILITIES = {
    "transcript": [
        "User stories — As a / I want / So that",
        "Business value statements",
        "Gherkin acceptance criteria",
        "Edge case and error scenarios",
        "Non-functional requirements",
        "Open questions and assumptions",
        "Stakeholder and role mapping",
        "Priority — High / Medium / Low",
    ],
    "refinement": [
        "INVEST criteria assessment (Pass / Warn / Fail)",
        "Issues found in original story",
        "Fully refined story",
        "Expanded edge-case coverage",
        "Open questions flagged",
        "Changes log with reasoning",
    ],
    "technical": [
        "Business + technical acceptance criteria",
        "API contracts (method, path, request, response)",
        "Error response mapping (4xx, 5xx)",
        "Data requirements and schema hints",
        "Integration point identification",
        "Security and performance NFRs",
        "GitHub code reference (when connected)",
    ],
    "solution": [
        "Component breakdown with tech choices",
        "API design table + key contracts",
        "Data model with field definitions",
        "Phased implementation roadmap",
        "Story dependency graph",
        "Technical risk register",
        "Codebase gap analysis (when connected)",
    ],
}


def render_mode(
    tab,
    mode_key: str,
    mode_label: str,
    badge: str,
    placeholder: str,
    btn_label: str,
    run_fn,
    input_height: int = 380,
    export_json: bool = True,
):
    with tab:
        st.markdown(
            f'<div class="mode-badge">{badge}</div>', unsafe_allow_html=True
        )
        col_in, col_out = st.columns([1, 1], gap="large")

        # ── Input column ──
        with col_in:
            st.markdown('<div class="sec-label">Input</div>', unsafe_allow_html=True)
            user_input = st.text_area(
                label="input",
                placeholder=placeholder,
                height=input_height,
                label_visibility="collapsed",
                key=f"input_{mode_key}",
            )
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            go = st.button(
                btn_label,
                type="primary",
                use_container_width=True,
                disabled=not (user_input or "").strip(),
                key=f"btn_{mode_key}",
            )
            if not (user_input or "").strip():
                st.markdown(
                    "<div style='font-size:0.78rem;color:#5E6C84;margin-top:6px;'>"
                    "Paste your input above to get started.</div>",
                    unsafe_allow_html=True,
                )

        # ── Output column ──
        with col_out:
            st.markdown('<div class="sec-label">Output</div>', unsafe_allow_html=True)

            result_key = f"result_{mode_key}"
            label_key = f"label_{mode_key}"

            if go and (user_input or "").strip():
                with st.spinner("Generating..."):
                    try:
                        github_ctx = get_github_context()
                        result = run_fn(user_input, github_ctx)
                        st.session_state[result_key] = result
                        st.session_state[label_key] = mode_label
                    except ValueError as exc:
                        st.error(f"Input error: {exc}")
                        st.stop()
                    except Exception as exc:
                        st.error(
                            f"Something went wrong. "
                            f"Check your GROQ_API_KEY in .env.\n\n{exc}"
                        )
                        st.stop()

            if result_key in st.session_state:
                result = st.session_state[result_key]
                stored_label = st.session_state.get(label_key, mode_label)

                st.markdown(
                    "<div class='success-banner'>Artifacts generated successfully.</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(result)

                # ── Export bar ──
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown(
                    "<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.1em;"
                    "text-transform:uppercase;color:#5E6C84;margin-bottom:10px;'>Export</div>",
                    unsafe_allow_html=True,
                )
                dl1, dl2 = st.columns(2)
                with dl1:
                    docx_bytes = markdown_to_docx(result, mode=stored_label)
                    st.download_button(
                        "Download .docx",
                        data=docx_bytes,
                        file_name=f"voxstory_{mode_key}.docx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument"
                            ".wordprocessingml.document"
                        ),
                        use_container_width=True,
                        key=f"docx_{mode_key}",
                    )
                with dl2:
                    if export_json:
                        json_bytes = to_json_bytes(result, mode=mode_key)
                        st.download_button(
                            "Download .json (Jira)",
                            data=json_bytes,
                            file_name=f"voxstory_{mode_key}.json",
                            mime="application/json",
                            use_container_width=True,
                            key=f"json_{mode_key}",
                        )
                    else:
                        st.download_button(
                            "Download .md",
                            data=result.encode("utf-8"),
                            file_name=f"voxstory_{mode_key}.md",
                            mime="text/markdown",
                            use_container_width=True,
                            key=f"md_{mode_key}",
                        )
            else:
                st.markdown(
                    "<div class='output-empty'>Your artifacts will appear here once generated.</div>",
                    unsafe_allow_html=True,
                )
                for cap in _CAPABILITIES.get(mode_key, []):
                    st.markdown(
                        f"<div class='cap-item'>{cap}</div>",
                        unsafe_allow_html=True,
                    )


# ── Collaboration Board ────────────────────────────────────────────────────────


def render_collab_board(tab):
    with tab:
        st.markdown(
            '<div class="mode-badge">Collaboration Board</div>',
            unsafe_allow_html=True,
        )

        session = st.session_state.get("collab_session")

        # ── No active session: create or load ─────────────────────────────────
        if session is None:
            col_create, col_load = st.columns([1, 1], gap="large")

            with col_create:
                st.markdown(
                    '<div class="sec-label">New Session</div>', unsafe_allow_html=True
                )
                st.markdown(
                    "<div style='font-size:0.84rem;color:#5E6C84;margin-bottom:1rem;'>"
                    "Start a new collaboration session. Multiple stakeholders add their "
                    "perspectives, and VoxStory synthesizes them into one unified story "
                    "and solution overview.</div>",
                    unsafe_allow_html=True,
                )
                project_name = st.text_input(
                    "Project Name",
                    placeholder="e.g. Customer Portal Redesign",
                    key="collab_project_name",
                )
                if st.button(
                    "Start Session",
                    type="primary",
                    disabled=not (project_name or "").strip(),
                    key="collab_start",
                    use_container_width=True,
                ):
                    st.session_state["collab_session"] = {
                        "session_id": str(uuid.uuid4()),
                        "session_name": project_name.strip(),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "contributions": [],
                        "synthesis_result": None,
                    }
                    st.rerun()

            with col_load:
                st.markdown(
                    '<div class="sec-label">Load Existing Session</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<div style='font-size:0.84rem;color:#5E6C84;margin-bottom:1rem;'>"
                    "Resume a previously downloaded session by uploading its JSON file.</div>",
                    unsafe_allow_html=True,
                )
                uploaded = st.file_uploader(
                    "Upload session JSON",
                    type=["json"],
                    label_visibility="collapsed",
                    key="collab_upload_initial",
                )
                if uploaded is not None:
                    data = _load_session_from_upload(uploaded)
                    if data:
                        st.session_state["collab_session"] = data
                        st.rerun()
            return

        # ── Active session ─────────────────────────────────────────────────────

        # Session header
        n_contribs = len(session["contributions"])
        st.markdown(
            f'<div class="collab-session-header">'
            f'<span class="collab-session-name">{session["session_name"]}</span>'
            f'<span class="collab-session-meta">'
            f'ID: {session["session_id"][:8]} &nbsp;·&nbsp; '
            f'Created: {session["created_at"][:10]} &nbsp;·&nbsp; '
            f'{n_contribs} contribution(s)'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Session actions row
        act1, act2, act3 = st.columns([3, 3, 2])
        with act1:
            session_json_str = json.dumps(session, indent=2, ensure_ascii=False)
            st.download_button(
                "Download Session (.json)",
                data=session_json_str.encode("utf-8"),
                file_name=f"session_{session['session_id'][:8]}.json",
                mime="application/json",
                use_container_width=True,
                key="collab_dl_session",
            )
        with act2:
            # Key tied to session_id so it resets when a new session is loaded
            uploaded_session = st.file_uploader(
                "Upload Session (.json)",
                type=["json"],
                label_visibility="collapsed",
                key=f"collab_upload_active_{session['session_id'][:8]}",
            )
            if uploaded_session is not None:
                data = _load_session_from_upload(uploaded_session)
                if data and data["session_id"] != session["session_id"]:
                    st.session_state["collab_session"] = data
                    st.rerun()
        with act3:
            if st.button(
                "New Session",
                type="secondary",
                use_container_width=True,
                key="collab_new_session",
            ):
                st.session_state["collab_session"] = None
                st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="large")

        # ── Left column: Add form + contributions list ─────────────────────────
        with col_left:
            st.markdown(
                '<div class="sec-label">Add Contribution</div>',
                unsafe_allow_html=True,
            )

            name_col, role_col = st.columns([3, 2])
            with name_col:
                contrib_name = st.text_input(
                    "Name",
                    placeholder="Full name",
                    key="collab_contrib_name",
                    label_visibility="collapsed",
                )
            with role_col:
                contrib_role = st.selectbox(
                    "Role",
                    options=ROLES,
                    key="collab_contrib_role",
                    label_visibility="collapsed",
                )

            contrib_text = st.text_area(
                "Perspective",
                placeholder=(
                    "Describe your perspective, requirements, or ideas...\n\n"
                    "What problem needs solving? What outcomes matter most to you? "
                    "What constraints or risks should the team know about?"
                ),
                height=180,
                key="collab_contrib_text",
                label_visibility="collapsed",
            )

            can_add = bool(
                (contrib_name or "").strip() and (contrib_text or "").strip()
            )
            if st.button(
                "Add Contribution",
                type="primary",
                disabled=not can_add,
                key="collab_add_btn",
                use_container_width=True,
            ):
                new_contrib = {
                    "id": str(uuid.uuid4()),
                    "name": contrib_name.strip(),
                    "role": contrib_role,
                    "text": contrib_text.strip(),
                    "added_at": datetime.now(timezone.utc).isoformat(),
                }
                session["contributions"].append(new_contrib)
                session["synthesis_result"] = None  # invalidate stale synthesis
                st.session_state["collab_session"] = session
                st.rerun()

            # Contributions list
            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
            n = len(session["contributions"])
            st.markdown(
                f'<div class="sec-label">Contributions ({n})</div>',
                unsafe_allow_html=True,
            )

            if n == 0:
                st.markdown(
                    "<div class='output-empty'>"
                    "No contributions yet. Add the first perspective above."
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                for c in session["contributions"]:
                    role_cls = ROLE_CSS_MAP.get(c["role"], "role-badge-other")
                    preview = (
                        c["text"] if len(c["text"]) <= 180 else c["text"][:177] + "..."
                    )
                    with st.container(border=True):
                        st.markdown(
                            f'<span class="role-badge {role_cls}">{c["role"]}</span>'
                            f'&nbsp;<strong style="font-size:0.88rem;color:#172B4D;">'
                            f'{c["name"]}</strong>'
                            f'<div style="font-size:0.81rem;color:#5E6C84;margin-top:6px;'
                            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;'
                            f'-webkit-box-orient:vertical;line-height:1.5;">'
                            f'{preview}</div>',
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            "Remove",
                            key=f"collab_rm_{c['id']}",
                            type="secondary",
                        ):
                            session["contributions"] = [
                                x for x in session["contributions"]
                                if x["id"] != c["id"]
                            ]
                            session["synthesis_result"] = None
                            st.session_state["collab_session"] = session
                            st.rerun()

        # ── Right column: Synthesize + output ─────────────────────────────────
        with col_right:
            st.markdown(
                '<div class="sec-label">Synthesis</div>', unsafe_allow_html=True
            )

            n = len(session["contributions"])
            can_synthesize = n >= 2

            if not can_synthesize:
                st.markdown(
                    "<div style='font-size:0.82rem;color:#5E6C84;margin-bottom:0.75rem;'>"
                    f"Add at least 2 contributions to enable synthesis. ({n} / 2)</div>",
                    unsafe_allow_html=True,
                )

            btn_label = (
                f"Synthesize All ({n} contributions)" if n > 0 else "Synthesize All"
            )
            if st.button(
                btn_label,
                type="primary",
                disabled=not can_synthesize,
                use_container_width=True,
                key="collab_synthesize_btn",
            ):
                contributions_text = _format_contributions(session["contributions"])
                github_ctx = get_github_context()
                with st.spinner("Synthesizing all perspectives..."):
                    try:
                        result = run_synthesis(contributions_text, github_ctx)
                        session["synthesis_result"] = result
                        st.session_state["collab_session"] = session
                    except Exception as exc:
                        st.error(
                            f"Synthesis failed. Check your GROQ_API_KEY in .env.\n\n{exc}"
                        )

            if session.get("synthesis_result"):
                st.markdown(
                    "<div class='success-banner'>"
                    "Synthesis complete — unified story and solution overview generated."
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(session["synthesis_result"])

                # Export
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown(
                    "<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.1em;"
                    "text-transform:uppercase;color:#5E6C84;margin-bottom:10px;'>"
                    "Export</div>",
                    unsafe_allow_html=True,
                )
                exp1, exp2 = st.columns(2)
                with exp1:
                    docx_bytes = markdown_to_docx(
                        session["synthesis_result"],
                        mode="Collaboration Synthesis",
                    )
                    st.download_button(
                        "Download .docx",
                        data=docx_bytes,
                        file_name=f"synthesis_{session['session_id'][:8]}.docx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument"
                            ".wordprocessingml.document"
                        ),
                        use_container_width=True,
                        key="collab_exp_docx",
                    )
                with exp2:
                    st.download_button(
                        "Download .md",
                        data=session["synthesis_result"].encode("utf-8"),
                        file_name=f"synthesis_{session['session_id'][:8]}.md",
                        mime="text/markdown",
                        use_container_width=True,
                        key="collab_exp_md",
                    )
            elif can_synthesize:
                st.markdown(
                    "<div class='output-empty'>"
                    "Click Synthesize All to generate a unified story and solution "
                    "overview from all contributions."
                    "</div>",
                    unsafe_allow_html=True,
                )


# ── Render each mode ───────────────────────────────────────────────────────────

render_mode(
    tab=tab_transcript,
    mode_key="transcript",
    mode_label="Transcript",
    badge="Transcript Mode",
    placeholder=(
        "Paste your meeting transcript, Zoom notes, or stakeholder discussion here.\n\n"
        "Example:\n"
        "PO: Users need to reset their passwords.\n"
        "Dev: What if the email doesn't exist?\n"
        "PO: Show a generic message — don't reveal if the account exists.\n"
        "BA: How long should the reset link be valid?\n"
        "PO: 24 hours. One-time use."
    ),
    btn_label="Extract User Stories",
    run_fn=run_transcript_mode,
)

render_mode(
    tab=tab_refine,
    mode_key="refinement",
    mode_label="Refinement",
    badge="Refinement Mode",
    placeholder=(
        "Paste a vague or incomplete user story to refine.\n\n"
        "Example:\n"
        "As a user, I want to log in so that I can use the system."
    ),
    btn_label="Refine Story",
    run_fn=run_refinement_mode,
    input_height=280,
)

render_mode(
    tab=tab_technical,
    mode_key="technical",
    mode_label="Technical",
    badge="Technical Story Mode",
    placeholder=(
        "Paste technical requirements, architecture notes, API specs, or a system design brief.\n\n"
        "Example:\n"
        "We need a REST endpoint that accepts a user ID and returns their order history "
        "from the orders service. It should use JWT auth, paginate results (max 50 per page), "
        "and support filtering by date range and status. The orders table has: id, user_id, "
        "status (pending/shipped/delivered/cancelled), total_amount, created_at."
    ),
    btn_label="Generate Technical Stories",
    run_fn=run_technical_mode,
    input_height=400,
)

render_mode(
    tab=tab_solution,
    mode_key="solution",
    mode_label="Solution Map",
    badge="Solution Map Mode",
    placeholder=(
        "Paste one or more user stories (or requirements) to map to a solution architecture.\n\n"
        "VoxStory will produce: component breakdown, API design, data model, "
        "implementation roadmap, story dependencies, and a technical risk register.\n\n"
        "Tip: connect a GitHub repo in the sidebar for a codebase-aware architecture map."
    ),
    btn_label="Generate Solution Map",
    run_fn=run_solution_mapping,
    input_height=400,
    export_json=False,
)

render_collab_board(tab_collab)
