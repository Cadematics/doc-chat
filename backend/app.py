import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Real Estate Disclosure RAG",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Real Estate Disclosure & Inspection Analyzer")
st.caption("Grounded Q&A with hierarchical parent-document retrieval and page-level citations")

# --- Sidebar: Document Management & Upload ---
with st.sidebar:
    st.header("1. Upload Disclosure PDF")
    uploaded_file = st.file_uploader("Drop a 300-page packet or inspection report", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Ingest & Index PDF", type="primary", use_container_width=True):
            with st.spinner(f"Parsing {uploaded_file.name} with LlamaParse (preserving tables & checkboxes)..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                res = requests.post(f"{API_URL}/upload", files=files, timeout=600)
                if res.ok:
                    data = res.json()
                    st.success(f"Indexed {data['file_name']} ({data['pages_indexed']} pages)")
                else:
                    st.error(f"Upload failed: {res.text}")

    st.divider()
    st.header("2. Indexed Documents")
    try:
        doc_res = requests.get(f"{API_URL}/documents", timeout=5)
        if doc_res.ok:
            docs = doc_res.json().get("documents", [])
            if docs:
                for d in docs:
                    st.markdown(f"- 📄 `{d}`")
            else:
                st.info("No PDFs found in `/docs` yet.")
    except requests.exceptions.ConnectionError:
        st.warning("FastAPI backend is offline. Start `uvicorn main:app --reload`.")

    st.divider()
    st.header("3. Quick Stress-Test Prompts")
    sample_prompts = [
        "Has the seller disclosed any past or present water penetration or roof leaks?",
        "What safety hazards were identified in the electrical panel or GFCI outlets?",
        "Are there any utility easements, liens, or shared driveway agreements on title?",
        "Does the HOA allow short-term rentals, and what are the pet restrictions?",
        "What is the remaining warranty on the solar panel inverters? (Negative test)",
    ]
    for q in sample_prompts:
        if st.button(q, use_container_width=True):
            st.session_state["prefill_question"] = q

# --- Main Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander(f"View {len(msg['citations'])} Grounded Source Citations"):
                for idx, cite in enumerate(msg["citations"], 1):
                    score_str = f" | Relevance: {cite['score']}" if cite.get("score") else ""
                    st.markdown(f"**[{idx}] `{cite['file_name']}` — Page {cite['page_number']}**{score_str}")
                    st.code(cite["snippet"], language="markdown")

prompt_input = st.chat_input("Ask a specific question about the property disclosures, title, HOA, or inspection...")
if "prefill_question" in st.session_state:
    prompt_input = st.session_state.pop("prefill_question")

if prompt_input:
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving parent sections and verifying citations..."):
            try:
                res = requests.post(
                    f"{API_URL}/ask",
                    json={"question": prompt_input},
                    timeout=120,
                )
                if res.ok:
                    payload = res.json()
                    answer = payload["answer"]
                    citations = payload.get("citations", [])
                    st.markdown(answer)
                    if citations:
                        with st.expander(f"View {len(citations)} Grounded Source Citations"):
                            for idx, cite in enumerate(citations, 1):
                                score_str = f" | Relevance: {cite['score']}" if cite.get("score") else ""
                                st.markdown(f"**[{idx}] `{cite['file_name']}` — Page {cite['page_number']}**{score_str}")
                                st.code(cite["snippet"], language="markdown")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "citations": citations}
                    )
                else:
                    st.error(f"Backend error: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach FastAPI backend at http://localhost:8000.")  