import html
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Disclosure AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Editorial CSS matching the Disclosure AI Design ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #111827;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.stApp {
    background-color: #FFFFFF;
}

/* --- Left Sidebar --- */
section[data-testid="stSidebar"] {
    background-color: #F9FAFB !important;
    border-right: 1px solid #E5E7EB !important;
    width: 280px !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Primary Dark Upload Button */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: #111827 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1rem !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    transition: background-color 0.15s ease;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background-color: #1F2937 !important;
}

/* Subtle Trash Delete Buttons in Sidebar */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: #9CA3AF !important;
    padding: 0.2rem 0.35rem !important;
    min-height: 0 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    color: #EF4444 !important;
    background-color: #FEE2E2 !important;
    border-radius: 6px !important;
}

/* Compact File Uploader Dropzone in Sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    padding: 0.65rem !important;
    background-color: #FFFFFF !important;
    border: 1px dashed #D1D5DB !important;
    border-radius: 8px !important;
}

/* --- Top Context Bar --- */
.top-context-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #F3F4F6;
    margin-bottom: 1.25rem;
    font-size: 0.85rem;
}

.context-left {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.badge-active {
    background-color: #EFF6FF;
    color: #2563EB;
    font-weight: 600;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
}

.context-right {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #6B7280;
    font-size: 0.8rem;
}

.status-pill-center {
    display: flex;
    justify-content: center;
    margin-bottom: 1.75rem;
}

.status-pill-center span {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    color: #4B5563;
    font-size: 0.75rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
}

/* --- Centered Chat Feed Container --- */
.main .block-container {
    max-width: 820px !important;
    padding-top: 0.5rem !important;
    padding-bottom: 6rem !important;
}

/* User Message Bubble (Right-Aligned Soft Slate/Blue-Gray) */
.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 1.25rem 0;
}

.user-bubble {
    background-color: #EEF2F6;
    color: #111827;
    padding: 0.85rem 1.15rem;
    border-radius: 14px;
    max-width: 72%;
    font-size: 0.93rem;
    line-height: 1.5;
}

/* Assistant Synthesis Block */
.synthesis-header {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    color: #6B7280;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.synthesis-body {
    font-size: 0.96rem;
    line-height: 1.65;
    color: #111827;
    margin-bottom: 0.85rem;
}

/* Citation Card & Primary Source Verification Box */
.findings-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.15rem;
    margin-top: 0.65rem;
    margin-bottom: 1.25rem;
}

.citation-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.citation-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 0.22rem 0.6rem;
    font-size: 0.76rem;
    font-weight: 500;
    color: #374151;
}

.verification-box {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
}

.verification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: #6B7280;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.confidence-tag {
    color: #111827;
    font-weight: 600;
    text-transform: none;
    letter-spacing: normal;
}

.verification-quote {
    font-style: italic;
    color: #374151;
    font-size: 0.84rem;
    line-height: 1.5;
    margin: 0;
}

/* Floating Pill Chat Input */
[data-testid="stChatInput"] {
    max-width: 780px;
    margin: 0 auto;
}

[data-testid="stChatInput"] > div {
    border-radius: 14px !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06) !important;
    background-color: #FFFFFF !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- Fetch Active Documents ---
docs = []
backend_online = True
try:
    doc_res = requests.get(f"{API_URL}/documents", timeout=5)
    if doc_res.ok:
        docs = doc_res.json().get("documents", [])
except requests.exceptions.ConnectionError:
    backend_online = False

# --- Left Sidebar ---
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:1rem;">
            <span style="font-size:1.15rem;">🏠</span>
            <span style="font-weight:700; font-size:1.05rem; color:#111827;">Disclosure AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        key=f"pdf_uploader_{st.session_state.uploader_key}",
    )
    if st.button("＋  Upload Document", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.toast("Select a PDF file above first.")
        else:
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                res = requests.post(f"{API_URL}/upload", files=files, timeout=600)
                if res.ok:
                    data = res.json()
                    st.session_state.uploader_key += 1
                    st.toast(f"Indexed {data['file_name']} ({data['pages_indexed']} pages)")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {res.text}")

    st.markdown(
        '<div style="font-size:0.7rem; font-weight:600; letter-spacing:0.06em; color:#6B7280; margin:1.35rem 0 0.6rem 0;">INDEXED DOCUMENTS</div>',
        unsafe_allow_html=True,
    )

    if not backend_online:
        st.warning("Backend offline (`uvicorn main:app --reload`)")
    elif not docs:
        st.caption("No documents uploaded yet.")
    else:
        for d in docs:
            c1, c2 = st.columns([0.84, 0.16], vertical_alignment="center")
            c1.markdown(
                f'<div style="font-size:0.83rem; color:#1F2937; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{html.escape(d)}">📄 {html.escape(d)}</div>',
                unsafe_allow_html=True,
            )
            if c2.button("🗑️", key=f"del_{d}", help=f"Delete {d}"):
                del_res = requests.delete(f"{API_URL}/documents/{d}", timeout=30)
                if del_res.ok:
                    st.toast(f"Deleted {d}")
                    st.rerun()
                else:
                    st.error(f"Failed: {del_res.text}")

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.76rem; color:#6B7280;">
            <div>
                <div style="font-weight:600; color:#111827;">Active Binder</div>
                <div>{len(docs)} file{"s" if len(docs) != 1 else ""} indexed</div>
            </div>
            <div style="font-weight:500;">RAG Grounded</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Top Header Bar ---
top_left, top_right = st.columns([0.75, 0.25], vertical_alignment="center")
with top_left:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.65rem; padding:0.4rem 0;">
            <span class="badge-active">● Active Context</span>
            <span style="font-weight:700; font-size:1rem; color:#111827;">Property Disclosure Binder</span>
            <span style="color:#6B7280; font-size:0.83rem;">· {len(docs)} files indexed &amp; grounded</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with top_right:
    if st.button("↻ New Analysis", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    '<div class="status-pill-center"><span>○ Deterministic RAG Engine Active · Zero exterior web hallucinations</span></div>',
    unsafe_allow_html=True,
)

# --- Render Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        safe_q = html.escape(msg["content"])
        st.markdown(
            f'<div class="user-row"><div class="user-bubble">{safe_q}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        citations = msg.get("citations", [])
        st.markdown(
            '<div class="synthesis-header"><span>▤ Synthesis</span> · <span>Grounded in indexed PDFs</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(msg["content"])

        if citations:
            pills_html = "".join(
                f'<span class="citation-pill">📄 {html.escape(str(c["file_name"]))} · p. {html.escape(str(c["page_number"]))}</span>'
                for c in citations
            )
            top_cite = citations[0]
            conf_str = (
                f"Match confidence: {round(top_cite['score'] * 100, 1)}%"
                if top_cite.get("score") is not None
                else "Verified excerpt"
            )
            excerpt = html.escape(top_cite["snippet"][:320].strip())

            st.markdown(
                f"""
                <div class="findings-card">
                    <div class="citation-pills">{pills_html}</div>
                    <div class="verification-box">
                        <div class="verification-header">
                            <span>PRIMARY SOURCE VERIFICATION · {html.escape(str(top_cite["file_name"]))} P. {html.escape(str(top_cite["page_number"]))}</span>
                            <span class="confidence-tag">{conf_str}</span>
                        </div>
                        <p class="verification-quote">"{excerpt}..."</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if len(citations) > 1:
                with st.expander(f"Inspect all {len(citations)} retrieved source excerpts"):
                    for idx, c in enumerate(citations, 1):
                        score_txt = f" ({round(c['score'] * 100, 1)}%)" if c.get("score") is not None else ""
                        st.markdown(f"**[{idx}] `{c['file_name']}` — Page {c['page_number']}{score_txt}**")
                        st.code(c["snippet"], language="markdown")

# --- Bottom Floating Input ---
prompt_input = st.chat_input("Ask anything about your uploaded property documents...")

if prompt_input:
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.spinner("Searching indexed documents & verifying page citations..."):
        try:
            res = requests.post(
                f"{API_URL}/ask",
                json={"question": prompt_input},
                timeout=120,
            )
            if res.ok:
                payload = res.json()
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": payload["answer"],
                        "citations": payload.get("citations", []),
                    }
                )
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Backend error: {res.text}", "citations": []}
                )
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Cannot reach FastAPI backend at `http://localhost:8000`.",
                    "citations": [],
                }
            )
    st.rerun()