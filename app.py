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

# Free tier: flash-lite ≈ 15 RPM / 500 RPD vs flash ≈ 5 RPM / 20 RPD
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
            blocks.append(f"<h2>{inline_format(stripped[3:])}</h2>")
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


st.set_page_config(
    page_title="Medi-Mind AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');

:root {
  --ink: #102a2e;
  --muted: #5a7278;
  --teal: #0f766e;
  --teal-deep: #0b4f4a;
  --line: rgba(16, 42, 46, 0.10);
  --panel: rgba(255, 255, 255, 0.78);
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(900px 420px at 8% -10%, rgba(15, 118, 110, 0.18), transparent 60%),
    radial-gradient(700px 380px at 100% 0%, rgba(180, 140, 90, 0.12), transparent 55%),
    linear-gradient(180deg, #f7f5f0 0%, #eef6f5 45%, #f4f7f6 100%);
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

#MainMenu, footer { visibility: hidden; }

.block-container {
  padding-top: 3.5rem !important;
  padding-bottom: 4rem !important;
  max-width: 1120px !important;
  overflow: visible !important;
}

section.main > div { overflow: visible !important; }

div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="column"] {
  overflow: visible !important;
}

.logo-wrap {
  margin: 0.35rem 0 0.85rem;
  overflow: visible;
}

.logo-wrap [data-testid="stImage"] img {
  display: block !important;
  object-fit: contain !important;
  max-height: 96px !important;
  width: auto !important;
  border-radius: 12px;
}

.scan-image [data-testid="stImage"] img {
  display: block !important;
  width: 100% !important;
  max-height: none !important;
  height: auto !important;
  object-fit: contain !important;
  border-radius: 12px;
  background: #0d1a1c;
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.35rem;
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(145deg, #12857c, #0b4f4a);
  color: #f4fffd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Fraunces', serif;
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.03em;
  box-shadow: 0 10px 24px rgba(15, 118, 110, 0.28);
}

.brand-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2rem, 4vw, 2.7rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.05;
  margin: 0;
  color: var(--ink);
}

.brand-sub {
  margin: 0.45rem 0 0;
  color: var(--muted);
  font-size: 1.02rem;
  max-width: 40rem;
  line-height: 1.5;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1.15rem 1.25rem 1.3rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 30px rgba(16, 42, 46, 0.05);
}

.panel-label {
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--teal);
  margin: 0 0 0.65rem;
}

.results-spacer {
  height: 1.25rem;
}

.report-box {
  background: rgba(255,255,255,0.92);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1.25rem 1.35rem 1.35rem;
  box-shadow: 0 12px 30px rgba(16, 42, 46, 0.05);
  margin-top: 0.35rem;
}

.report-box h2 {
  font-family: 'Fraunces', serif;
  font-size: 1.18rem;
  color: var(--teal-deep);
  margin: 1.15rem 0 0.45rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.35rem;
}

.report-box h2:first-child { margin-top: 0; }

.report-box p, .report-box li {
  color: #24383c;
  line-height: 1.55;
  font-size: 0.98rem;
}

.report-box ul {
  margin: 0.35rem 0 0.7rem 1.1rem;
  padding: 0;
}

.report-box p { margin: 0.35rem 0 0.55rem; }

.notice {
  margin-top: 0.9rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: #fff7e8;
  border: 1px solid rgba(180, 120, 40, 0.25);
  color: #6a4a18;
  font-size: 0.92rem;
  line-height: 1.45;
}

.empty-hint {
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

div[data-testid="stFileUploader"] section {
  background: rgba(255,255,255,0.55);
  border: 1.5px dashed rgba(15, 118, 110, 0.35) !important;
  border-radius: 14px;
  padding: 0.5rem;
}

div[data-testid="stFileUploader"] section:hover {
  border-color: rgba(15, 118, 110, 0.65) !important;
  background: rgba(231, 244, 242, 0.65);
}

.stButton > button {
  background: linear-gradient(145deg, #12857c, #0b4f4a) !important;
  color: #f4fffd !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.7rem 1.4rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  box-shadow: 0 10px 22px rgba(15, 118, 110, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button:hover {
  box-shadow: 0 14px 26px rgba(15, 118, 110, 0.32);
  color: #fff !important;
}

@media (max-width: 768px) {
  .brand-title { font-size: 1.85rem; }
  .block-container { padding-top: 3rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

logo_path = Path("./images/Logo.jpg")
if logo_path.exists():
    st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
    st.image(str(logo_path), width=200)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <p class="brand-sub">Upload a medical scan and get a structured AI reading — findings, next steps, and precautions. For support only, not a clinical diagnosis.</p>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="brand-wrap">
          <div class="brand-mark">M</div>
          <h1 class="brand-title">Medi-Mind AI</h1>
        </div>
        <p class="brand-sub">Upload a medical scan and get a structured AI reading — findings, next steps, and precautions. For support only, not a clinical diagnosis.</p>
        """,
        unsafe_allow_html=True,
    )

st.write("")

upload_col, action_col = st.columns([2.2, 1], gap="large")

with upload_col:
    st.markdown(
        '<div class="panel-label">Scan upload</div>',
        unsafe_allow_html=True,
    )
    upload_file = st.file_uploader(
        "Drop a medical image here",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        help="Supported: PNG, JPG, JPEG",
    )

with action_col:
    st.markdown(
        '<div class="panel-label">Action</div>',
        unsafe_allow_html=True,
    )
    st.caption("Ready when an image is selected.")
    analyze = st.button("Analyze image", use_container_width=True, type="primary")

if "last_report" not in st.session_state:
    st.session_state.last_report = None
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_name" not in st.session_state:
    st.session_state.last_name = None

if analyze:
    if upload_file is None:
        st.warning("Please upload a medical image first.")
    elif not model:
        st.error(
            "API key missing. For local use put it in `api_key.py`. "
            "On Streamlit Cloud add secret `GEMINI_API_KEY`."
        )
    else:
        image_data = upload_file.getvalue()
        mime = upload_file.type or "image/jpeg"
        prompt_part = [
            {"mime_type": mime, "data": image_data},
            system_prompt,
        ]

        with st.spinner("Reading the scan…"):
            try:
                response = model.generate_content(prompt_part)
                st.session_state.last_report = (response.text or "").strip()
                st.session_state.last_image = image_data
                st.session_state.last_name = upload_file.name
            except Exception as exc:
                message = str(exc)
                if "429" in message or "ResourceExhausted" in message or "quota" in message.lower():
                    st.error("Free-tier rate limit reached. Wait about a minute, then try once more.")
                elif "API key" in message or "API_KEY" in message:
                    st.error("API key is missing or invalid.")
                else:
                    st.error(f"Analysis failed: {message}")

if st.session_state.last_image is not None and st.session_state.last_report:
    st.markdown('<div class="results-spacer"></div>', unsafe_allow_html=True)
    st.divider()
    left, right = st.columns([1, 1.25], gap="large")

    with left:
        name = html.escape(st.session_state.last_name or "Uploaded image")
        st.markdown(
            f"""
            <div class="panel">
              <div class="panel-label">Uploaded scan</div>
              <p style="margin:0 0 0.75rem;color:var(--muted);font-size:0.9rem;">{name}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="scan-image">', unsafe_allow_html=True)
        st.image(st.session_state.last_image, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            f"""
            <div class="panel-label">AI clinical report</div>
            <div class="report-box">
              {report_to_html(st.session_state.last_report)}
            </div>
            <div class="notice"><strong>Important:</strong> Medi-Mind AI is informational only. Always consult a licensed clinician before any medical decision.</div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="panel" style="margin-top:1rem;">
          <p class="empty-hint">Your analyzed scan and structured report will appear here side by side after you click <strong>Analyze image</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
