import base64
import html
import os
import re
from pathlib import Path

import google.generativeai as genai
import streamlit as st


def get_api_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key

    try:
        from api_key import api_key as local_key

        if local_key and local_key not in ("YOUR_API_KEY", ""):
            return local_key
    except ImportError:
        pass

    return None


api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompt = """
As a highly skilled medical practitioner specializing in image analysis, examine the medical image carefully.

Respond in clean Markdown with exactly these sections (use ## headings):

## Detailed Analysis
Thoroughly analyze the image. Note modality if clear, and describe abnormal or normal findings.

## Findings Report
Document anomalies or disease signs in a clear structured impression.

## Recommendations
Suggest next steps: further tests, clinical correlation, or follow-up as applicable.

## Treatment Suggestions
Recommend possible treatments or interventions only if appropriate; otherwise say none indicated.

Rules:
1. Only respond if the image relates to human health.
2. If image quality is poor, say what cannot be determined.
3. End with: **Disclaimer:** Consult a doctor before making any decisions.
4. Be concise, clinical, and structured. Do not add a title before the first ## heading.
"""

model = None
if api_key:
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash-lite",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )


def inline_format(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def report_to_html(text: str) -> str:
    blocks: list[str] = []
    in_list = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("## "):
            if in_list:
                blocks.append("</ul>")
                in_list = False
            blocks.append(f"<h3>{inline_format(stripped[3:])}</h3>")
            continue

        if stripped.startswith(("- ", "* ")):
            if not in_list:
                blocks.append("<ul>")
                in_list = True
            blocks.append(f"<li>{inline_format(stripped[2:])}</li>")
            continue

        if not stripped:
            if in_list:
                blocks.append("</ul>")
                in_list = False
            continue

        if in_list:
            blocks.append("</ul>")
            in_list = False
        blocks.append(f"<p>{inline_format(stripped)}</p>")

    if in_list:
        blocks.append("</ul>")

    return "\n".join(blocks)


def to_data_uri(data: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


st.set_page_config(
    page_title="MediMind — Image Review",
    page_icon="images/Logo.jpg" if Path("images/Logo.jpg").exists() else None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@500;600&display=swap');

:root {
  --ink: #10232b;
  --muted: #4d6670;
  --line: #6f8f9a;
  --line-soft: #9bb4bc;
  --surface: #f3f8f9;
  --surface-2: #e7f1f3;
  --accent: #0f7c6e;
  --accent-deep: #0b5a50;
  --navy: #0d3640;
  --viewer: #0a1519;
  --warn-bg: #fff4df;
  --warn-ink: #6a4d1d;
  --warn-line: #d9b56a;
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(900px 420px at 0% 0%, rgba(15, 124, 110, 0.18), transparent 55%),
    radial-gradient(800px 380px at 100% 10%, rgba(30, 90, 120, 0.16), transparent 50%),
    linear-gradient(165deg, #c5d8de 0%, #d7e6ea 42%, #cfdfe4 100%);
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

#MainMenu, footer { visibility: hidden; }

.block-container {
  padding-top: 2.75rem !important;
  padding-bottom: 3rem !important;
  max-width: 1200px !important;
  overflow: visible !important;
}

section.main > div,
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="column"] {
  overflow: visible !important;
  gap: 0.85rem !important;
}

.app-shell {
  border: 2px solid #4f737d;
  border-radius: 14px;
  background: linear-gradient(180deg, #123c46 0%, #0d3038 100%);
  padding: 0.95rem 1.05rem 1.05rem;
  box-shadow: 0 18px 40px rgba(10, 35, 42, 0.22);
  margin-bottom: 0.95rem;
}

.app-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.app-bar-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-width: 0;
}

.app-bar-logo {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid #6f98a3;
  background: #071318;
  flex-shrink: 0;
}

.app-bar-copy h1 {
  margin: 0;
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #edf7f8;
  line-height: 1.15;
}

.app-bar-copy p {
  margin: 0.15rem 0 0;
  color: #9fc0c8;
  font-size: 0.84rem;
  line-height: 1.35;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 2px solid #6f98a3;
  background: rgba(231, 241, 243, 0.12);
  color: #d7ecef;
  border-radius: 999px;
  padding: 0.34rem 0.78rem;
  font-size: 0.76rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-chip.ok { border-color: #3dbf8f; }
.status-chip.bad { border-color: #e0a35d; color: #ffe3bd; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3dbf8f;
}

.status-chip.bad .status-dot { background: #e0a35d; }

.control-strip {
  background: var(--surface);
  border: 2px solid #6f8f9a;
  border-radius: 10px;
  padding: 0.85rem 0.95rem 0.95rem;
}

.section-title {
  margin: 0 0 0.55rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: #355860;
}

.pane {
  background: var(--surface);
  border: 2px solid #5f818c;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 24px rgba(16, 45, 52, 0.10);
  min-height: 430px;
}

.pane-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.78rem 0.95rem;
  border-bottom: 2px solid #b7cdd4;
  background: linear-gradient(180deg, #eaf4f6 0%, #ddecef 100%);
}

.pane-head h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--navy);
}

.pane-meta {
  color: #4d6670;
  font-size: 0.76rem;
  font-weight: 500;
}

.viewer-body {
  background: radial-gradient(circle at 50% 35%, #1a2d35 0%, var(--viewer) 70%);
  min-height: 360px;
  padding: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-body img {
  width: 100%;
  max-height: 480px;
  object-fit: contain;
  border-radius: 6px;
  border: 2px solid #2d4650;
}

.report-body {
  padding: 1rem 1.1rem 1.2rem;
  background: linear-gradient(180deg, #f7fbfc 0%, #eef6f7 100%);
}

.report-body h3 {
  margin: 1.05rem 0 0.4rem;
  font-family: 'IBM Plex Serif', serif;
  font-size: 1.04rem;
  font-weight: 600;
  color: #0f3d48;
  border-bottom: 2px solid #b9d0d6;
  padding-bottom: 0.3rem;
}

.report-body h3:first-child { margin-top: 0; }

.report-body p,
.report-body li {
  color: #243841;
  font-size: 0.93rem;
  line-height: 1.55;
}

.report-body ul {
  margin: 0.25rem 0 0.65rem 1.05rem;
  padding: 0;
}

.report-body p { margin: 0.3rem 0 0.5rem; }

.empty-pane {
  padding: 2.6rem 1.5rem;
  color: #5a7380;
  font-size: 0.94rem;
  line-height: 1.6;
  text-align: center;
  background: linear-gradient(180deg, #f2f8f9 0%, #e4eef1 100%);
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.disclaimer {
  margin-top: 0.85rem;
  border: 2px solid var(--warn-line);
  background: var(--warn-bg);
  color: var(--warn-ink);
  border-radius: 10px;
  padding: 0.8rem 0.95rem;
  font-size: 0.86rem;
  line-height: 1.45;
}

div[data-testid="stFileUploader"] section {
  background: #eef6f7 !important;
  border: 2px dashed #6f8f9a !important;
  border-radius: 8px !important;
  padding: 0.4rem;
}

div[data-testid="stFileUploader"] section:hover {
  border-color: var(--accent) !important;
  background: #e4f3f0 !important;
}

.stButton > button {
  background: var(--accent) !important;
  color: #f3fffc !important;
  border: 2px solid var(--accent-deep) !important;
  border-radius: 8px !important;
  padding: 0.62rem 1rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
  min-height: 2.7rem;
}

.stButton > button:hover {
  background: var(--accent-deep) !important;
  color: #fff !important;
}

@media (max-width: 900px) {
  .app-bar { flex-direction: column; align-items: flex-start; }
  .block-container { padding-top: 2.2rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

logo_path = Path("images/Logo.jpg")
if logo_path.exists():
    logo_html = f'<img class="app-bar-logo" src="{to_data_uri(logo_path.read_bytes())}" alt="MediMind" />'
else:
    logo_html = (
        '<div class="app-bar-logo" style="display:flex;align-items:center;justify-content:center;'
        'color:#9fc0c8;font-size:0.72rem;font-weight:700;">MM</div>'
    )

if api_key:
    status_html = '<div class="status-chip ok"><span class="status-dot"></span>API connected</div>'
else:
    status_html = '<div class="status-chip bad"><span class="status-dot"></span>API key missing</div>'

st.markdown(
    f"""
    <div class="app-shell">
      <div class="app-bar">
        <div class="app-bar-left">
          {logo_html}
          <div class="app-bar-copy">
            <h1>MediMind</h1>
            <p>Medical image review workspace</p>
          </div>
        </div>
        {status_html}
      </div>
      <div class="control-strip">
        <p class="section-title">Study input</p>
    """,
    unsafe_allow_html=True,
)

upload_col, action_col = st.columns([2.4, 1], gap="medium")
with upload_col:
    upload_file = st.file_uploader(
        "Upload scan",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        help="PNG, JPG, or JPEG",
    )
with action_col:
    st.write("")
    analyze = st.button("Run analysis", use_container_width=True, type="primary")

st.markdown("</div></div>", unsafe_allow_html=True)

if "last_report" not in st.session_state:
    st.session_state.last_report = None
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_name" not in st.session_state:
    st.session_state.last_name = None
if "last_mime" not in st.session_state:
    st.session_state.last_mime = "image/jpeg"

if analyze:
    if upload_file is None:
        st.warning("Upload a medical image before running analysis.")
    elif not model:
        st.error(
            "API key missing. Local: set it in `api_key.py`. "
            "Streamlit Cloud: add secret `GEMINI_API_KEY`."
        )
    else:
        image_data = upload_file.getvalue()
        mime = upload_file.type or "image/jpeg"
        prompt_part = [
            {"mime_type": mime, "data": image_data},
            system_prompt,
        ]

        with st.spinner("Analyzing study…"):
            try:
                response = model.generate_content(prompt_part)
                st.session_state.last_report = (response.text or "").strip()
                st.session_state.last_image = image_data
                st.session_state.last_name = upload_file.name
                st.session_state.last_mime = mime
            except Exception as exc:
                message = str(exc)
                if "429" in message or "ResourceExhausted" in message or "quota" in message.lower():
                    st.error("Rate limit reached. Wait about a minute, then try once.")
                elif "API key" in message or "API_KEY" in message:
                    st.error("API key is missing or invalid.")
                else:
                    st.error(f"Analysis failed: {message}")

has_result = st.session_state.last_image is not None and st.session_state.last_report
name = html.escape(st.session_state.last_name or "No study loaded")

viewer_col, report_col = st.columns([0.95, 1.15], gap="medium")

with viewer_col:
    if has_result:
        img_uri = to_data_uri(st.session_state.last_image, st.session_state.last_mime)
        st.markdown(
            f"""
            <div class="pane">
              <div class="pane-head">
                <h2>Image viewer</h2>
                <span class="pane-meta">{name}</span>
              </div>
              <div class="viewer-body">
                <img src="{img_uri}" alt="Uploaded medical scan" />
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="pane">
              <div class="pane-head">
                <h2>Image viewer</h2>
                <span class="pane-meta">{name}</span>
              </div>
              <div class="empty-pane">Upload a scan and run analysis to open the study in the viewer.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with report_col:
    if has_result:
        st.markdown(
            f"""
            <div class="pane">
              <div class="pane-head">
                <h2>Clinical report</h2>
                <span class="pane-meta">Draft • AI assisted</span>
              </div>
              <div class="report-body">
                {report_to_html(st.session_state.last_report)}
              </div>
            </div>
            <div class="disclaimer"><strong>Clinical use disclaimer:</strong> Informational support only. Not a substitute for licensed medical judgment.</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="pane">
              <div class="pane-head">
                <h2>Clinical report</h2>
                <span class="pane-meta">Waiting</span>
              </div>
              <div class="empty-pane">Findings, impression, recommendations, and precautions will appear here after analysis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
