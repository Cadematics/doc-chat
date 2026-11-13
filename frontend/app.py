import os
import html
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Doc-Chat",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Editorial Light UI Matching Reference Mockup ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #111827 !important;
}

/* Hide Streamlit chrome while keeping sidebar toggle reachable */
#MainMenu, footer {
    visibility: hidden;
    height: 0;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Pure White Main Canvas */
.stApp, [data-testid="stAppViewContainer"], .main {
    background-color: #FFFFFF !important;
}

/* Bottom Bar Area */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #FFFFFF !important;
    border-top: none !important;
}

/* --- Left Sidebar --- */
section[data-testid="stSidebar"] {
    background-color: #FAFAFA !important;
    border-right: 1px solid #ECEEF2 !important;
    min-width: 270px !important;
    max-width: 270px !important;
    transform: none !important;
    visibility: visible !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.15rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Compact File Uploader in Sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #6B7280 !important;
    margin-bottom: 0.25rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
    border: 1px dashed #D1D5DB !important;
    border-radius: 8px !important;
    padding: 0.55rem 0.65rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] div {
    color: #4B5563 !important;
    font-size: 0.76rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.75rem !important;
    padding: 0.2rem 0.55rem !important;
}

/* Primary Solid Black Upload Button (+ Upload documents) */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: #18181B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    padding: 0.5rem 0.9rem !important;
    margin-top: 0.25rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background-color: #27272A !important;
}

/* Subtle Delete Button next to Indexed Documents */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: #9CA3AF !important;
    border-radius: 6px !important;
    padding: 0.1rem 0.35rem !important;
    min-height: 26px !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #FEE2E2 !important;
    color: #DC2626 !important;
}

/* Document Row Styling */
.doc-item-row {
    background-color: #EFF6FF;
    border-radius: 7px;
    padding: 0.42rem 0.6rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: #1E293B;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* --- Centered Chat Container --- */
.main .block-container {
    max-width: 820px !important;
    padding-top: 0.65rem !important;
    padding-bottom: 7.5rem !important;
}

/* Flat Top Context Bar */
.top-context-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0.25rem 0.85rem 0.25rem;
    border-bottom: 1px solid #F1F5F9;
}

.top-context-left {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.badge-active {
    background-color: #EEF2FF;
    color: #2563EB;
    font-weight: 600;
    font-size: 0.73rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
}

.top-context-right {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: #4B5563;
    font-size: 0.8rem;
    font-weight: 500;
}

/* Centered RAG Engine Pill */
.status-pill-center {
    display: flex;
    justify-content: center;
    margin: 1.15rem 0 1.75rem 0;
}

.status-pill-center span {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #475569;
    font-size: 0.74rem;
    font-weight: 500;
    padding: 0.28rem 0.85rem;
    border-radius: 999px;
}

/* Right-Aligned Soft Blue-Slate User Bubble */
.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 1.25rem 0 1.5rem 0;
}

.user-bubble {
    background-color: #E8EEF5;
    color: #1E293B;
    padding: 0.85rem 1.15rem;
    border-radius: 14px;
    max-width: 72%;
    font-size: 0.92rem;
    font-weight: 400;
    line-height: 1.5;
}

/* Borderless Editorial Synthesis Header */
.synthesis-header {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.78rem;
    color: #6B7280;
    margin-bottom: 0.55rem;
}

.synthesis-header strong {
    color: #111827;
    font-weight: 600;
}

/* Findings Card & Primary Source Verification Box */
.findings-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0.95rem 1.1rem;
    margin-top: 0.4rem;
}

.citation-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 0.75rem;
}

.citation-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.22rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: #334155;
}

.verification-box {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 0.8rem 0.95rem;
}

.verification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #6B7280;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
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

/* Floating Prompt Input */
[data-testid="stChatInput"] {
    max-width: 780px;
    margin: 0 auto;
}

[data-testid="stChatInput"] > div {
    border-radius: 14px !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06) !important;
    background-color: #FFFFFF !important;
}

[data-testid="stChatInput"] textarea {
    color: #111827 !important;
    background-color: #FFFFFF !important;
    font-size: 0.92rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #9CA3AF !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    background-color: #18181B !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
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
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.9rem;">
            <span style="font-size:1.15rem;">🏠</span>
            <span style="font-weight:700; font-size:1.05rem; color:#111827;">Doc-Chat</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Find document",
        type=["pdf"],
        label_visibility="visible",
        key=f"pdf_uploader_{st.session_state.uploader_key}",
    )
    if st.button("＋  Upload documents", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.toast("Select a PDF file in the box above first.")
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
        '<div style="font-size:0.68rem; font-weight:700; letter-spacing:0.06em; color:#6B7280; margin:1.25rem 0 0.55rem 0;">INDEXED DOCUMENTS</div>',
        unsafe_allow_html=True,
    )

    if not backend_online:
        st.warning("Backend offline (`uvicorn main:app --reload`)")
    elif not docs:
        st.caption("No documents uploaded yet.")
    else:
        for d in docs:
            c1, c2 = st.columns([0.85, 0.15], vertical_alignment="center")
            c1.markdown(
                f'<div class="doc-item-row" title="{html.escape(d)}">📄 {html.escape(d)}</div>',
                unsafe_allow_html=True,
            )
            if c2.button("✕", key=f"del_{d}", help=f"Remove {d}"):
                del_res = requests.delete(f"{API_URL}/documents/{d}", timeout=30)
                if del_res.ok:
                    st.toast(f"Deleted {d}")
                    st.rerun()
                else:
                    st.error(f"Failed: {del_res.text}")

    st.markdown("<div style='height: 3.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="border-top:1px solid #ECEEF2; padding-top:0.75rem; display:flex; justify-content:space-between; align-items:flex-end; font-size:0.75rem; color:#6B7280;">
            <div>
                <div style="font-weight:600; color:#111827;">Active Binder</div>
                <div>{len(docs)} file{"s" if len(docs) != 1 else ""} indexed</div>
            </div>
            <div style="font-weight:500; color:#4B5563;">Grounded</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Top Context Header ---
st.markdown(
    f"""
    <div class="top-context-bar">
        <div class="top-context-left">
            <span class="badge-active">● Active Context</span>
            <span style="font-weight:700; font-size:0.96rem; color:#111827;">Property Disclosure Binder</span>
        </div>
        <div class="top-context-right">
            <span>✓ {len(docs)} file{"s" if len(docs) != 1 else ""} indexed &amp; grounded</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="status-pill-center"><span>○ RAG engine</span></div>',
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
            '<div class="synthesis-header"><span>▤</span> <strong>Synthesis</strong> · <span>Grounded in indexed PDFs</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(msg["content"])

        if citations:
            pills_html = "".join(
                f'<span class="citation-pill">📄 {html.escape(str(c["file_name"]))} · p. {html.escape(str(c["page_number"]))}</span>'
                for c in citations
            )
            top_cite = citations[0]
            excerpt = html.escape(top_cite["snippet"][:320].strip())
            label = (
                f"View primary source verification & all {len(citations)} retrieved excerpts"
                if len(citations) > 1
                else "View primary source verification"
            )

            with st.expander(label, expanded=False):
                st.markdown(
                    f"""
                    <div class="findings-card" style="margin-top:0; margin-bottom:0.75rem;">
                        <div class="citation-pills">{pills_html}</div>
                        <div class="verification-box">
                            <div class="verification-header">
                                <span>PRIMARY SOURCE VERIFICATION · {html.escape(str(top_cite["file_name"]))} P. {html.escape(str(top_cite["page_number"]))}</span>
                                <span class="confidence-tag">Verified source excerpt</span>
                            </div>
                            <p class="verification-quote">"{excerpt}..."</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if len(citations) > 1:
                    for idx, c in enumerate(citations, 1):
                        st.markdown(f"**[{idx}] `{c['file_name']}` — Page {c['page_number']}**")
                        st.code(c["snippet"], language="markdown")

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# --- Bottom Floating Input ---
prompt_input = st.chat_input("Ask anything about your uploaded property documents...")

if prompt_input:
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-6:]
    ]
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.spinner("Searching indexed documents & verifying page citations..."):
        try:
            res = requests.post(
                f"{API_URL}/ask",
                json={"question": prompt_input, "chat_history": history_payload},
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
                    "content": f"Cannot reach FastAPI backend at `{API_URL}`.",
                    "citations": [],
                }
            )
    st.rerun()