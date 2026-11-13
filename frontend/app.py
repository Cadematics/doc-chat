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

# --- High-Contrast Light Editorial CSS ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A !important;
}

/* Hide menu/footer but keep sidebar expand button reachable */
#MainMenu, footer {
    visibility: hidden;
    height: 0;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Soft Cool-Gray Main Canvas */
.stApp, [data-testid="stAppViewContainer"], .main {
    background-color: #F8FAFC !important;
}

/* Bottom Bar Container */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #F8FAFC !important;
    border-top: 1px solid #E2E8F0 !important;
}

/* --- Left Sidebar (Always Visible & Distinct Cool Slate Tint) --- */
section[data-testid="stSidebar"] {
    background-color: #F1F5F9 !important;
    border-right: 1px solid #CBD5E1 !important;
    min-width: 295px !important;
    max-width: 295px !important;
    transform: none !important;
    visibility: visible !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* File Uploader Label & Box in Sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    margin-bottom: 0.25rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
    border: 1.5px dashed #94A3B8 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] div {
    color: #334155 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

/* Primary Dark Upload Action Button */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1rem !important;
    margin-top: 0.35rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background-color: #0F172A !important;
}

/* Clean Light Delete Button next to each Document */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #64748B !important;
    border-radius: 6px !important;
    padding: 0.15rem 0.45rem !important;
    min-height: 28px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #FEF2F2 !important;
    border-color: #FECACA !important;
    color: #DC2626 !important;
}

/* Document Row Card in Sidebar */
.doc-item-pill {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.45rem 0.65rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: #0F172A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* --- Centered Chat Container --- */
.main .block-container {
    max-width: 840px !important;
    padding-top: 0.75rem !important;
    padding-bottom: 6.5rem !important;
}

/* Top Header Card */
.top-header-box {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0.75rem 1.15rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}

.badge-active {
    background-color: #DBEAFE;
    color: #1D4ED8;
    font-weight: 600;
    font-size: 0.75rem;
    padding: 0.22rem 0.65rem;
    border-radius: 999px;
}

.status-pill-center {
    display: flex;
    justify-content: center;
    margin: 1.1rem 0 1.6rem 0;
}

.status-pill-center span {
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1E40AF;
    font-size: 0.76rem;
    font-weight: 500;
    padding: 0.32rem 0.95rem;
    border-radius: 999px;
}

/* User Message Bubble */
.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 1.15rem 0;
}

.user-bubble {
    background-color: #DBEAFE;
    border: 1px solid #BFDBFE;
    color: #0F172A;
    padding: 0.85rem 1.15rem;
    border-radius: 14px 14px 4px 14px;
    max-width: 74%;
    font-size: 0.94rem;
    font-weight: 500;
    line-height: 1.5;
}

/* Assistant Response Card */
.assistant-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.synthesis-header {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    color: #475569;
    margin-bottom: 0.6rem;
    font-weight: 600;
}

/* Citation Card & Primary Source Verification Box */
.findings-card {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    padding: 0.9rem 1.05rem;
    margin-top: 0.85rem;
}

.citation-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 0.7rem;
}

.citation-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 6px;
    padding: 0.22rem 0.6rem;
    font-size: 0.76rem;
    font-weight: 600;
    color: #1E40AF;
}

.verification-box {
    background-color: #FFFFFF;
    border-left: 3px solid #2563EB;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.8rem 0.95rem;
}

.verification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #475569;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.confidence-tag {
    background-color: #DCFCE7;
    color: #166534;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    font-weight: 600;
    text-transform: none;
    letter-spacing: normal;
}

.verification-quote {
    font-style: italic;
    color: #1E293B;
    font-size: 0.85rem;
    line-height: 1.5;
    margin: 0;
}

/* Readable High-Contrast Chat Input Box */
[data-testid="stChatInput"] {
    max-width: 800px;
    margin: 0 auto;
}

[data-testid="stChatInput"] > div {
    border-radius: 12px !important;
    border: 1.5px solid #94A3B8 !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
    background-color: #FFFFFF !important;
}

[data-testid="stChatInput"] textarea {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    font-size: 0.94rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    background-color: #2563EB !important;
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
        <div style="display:flex; align-items:center; gap:0.55rem; margin-bottom:1rem;">
            <span style="font-size:1.25rem;">🏠</span>
            <span style="font-weight:700; font-size:1.1rem; color:#0F172A;">Doc-Chat</span>
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
        '<div style="font-size:0.72rem; font-weight:700; letter-spacing:0.06em; color:#475569; margin:1.35rem 0 0.6rem 0;">INDEXED DOCUMENTS</div>',
        unsafe_allow_html=True,
    )

    if not backend_online:
        st.warning("Backend offline (`uvicorn main:app --reload`)")
    elif not docs:
        st.info("No documents uploaded yet.")
    else:
        for d in docs:
            c1, c2 = st.columns([0.82, 0.18], vertical_alignment="center")
            c1.markdown(
                f'<div class="doc-item-pill" title="{html.escape(d)}">📄 {html.escape(d)}</div>',
                unsafe_allow_html=True,
            )
            if c2.button("✕", key=f"del_{d}", help=f"Remove {d}"):
                del_res = requests.delete(f"{API_URL}/documents/{d}", timeout=30)
                if del_res.ok:
                    st.toast(f"Deleted {d}")
                    st.rerun()
                else:
                    st.error(f"Failed: {del_res.text}")

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:0.65rem 0.8rem; display:flex; justify-content:space-between; align-items:center; font-size:0.78rem; color:#475569;">
            <div>
                <div style="font-weight:700; color:#0F172A;">Active Binder</div>
                <div>{len(docs)} file{"s" if len(docs) != 1 else ""} indexed</div>
            </div>
            <span style="background:#DCFCE7; color:#166534; font-weight:600; font-size:0.7rem; padding:0.18rem 0.5rem; border-radius:999px;">Grounded</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Top Header Bar ---
st.markdown(
    f"""
    <div class="top-header-box">
        <span class="badge-active">● Active Context</span>
        <span style="font-weight:700; font-size:0.98rem; color:#0F172A;">Property Disclosure Binder</span>
        <span style="color:#475569; font-size:0.83rem;">· {len(docs)} file{"s" if len(docs) != 1 else ""} indexed &amp; grounded</span>
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
        with st.container():
            st.markdown(
                '<div class="assistant-card"><div class="synthesis-header"><span>▤ Synthesis</span> · <span>Grounded in indexed PDFs</span></div>',
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

            st.markdown("</div>", unsafe_allow_html=True)

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