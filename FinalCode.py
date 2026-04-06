import streamlit as st
from langchain_groq import ChatGroq 
from pypdf import PdfReader
import os

# ── PAGE CONFIG ─────────────────────────────
st.set_page_config(page_title="PrepGuideX AI", page_icon="📘", layout="wide")

# ── CSS ─────────────────────────────
st.markdown("""
<style>
.stApp {
    background: #0a0d1f;
    font-family: 'Inter', sans-serif;
}

/* 🔥 FIX CROWDING */
.block-container {
    max-width: 1300px;
    padding-top: 60px;
}

/* HEADER */
.pgx-header {
    display: flex;
    align-items: flex-start;
    gap: 18px;
    margin-bottom: 50px;
}
.pgx-header-icon {
    font-size: 50px;
}
.pgx-header-text h1 {
    color: white;
    font-size: 46px;
    font-weight: 800;
    margin: 0;
}
.pgx-caption {
    color: #6b7280;
    font-size: 18px;
    margin-top: 6px;
    margin-left: 10px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: #6b7280;
    border-radius: 12px;
    padding: 18px;
}

/* 🔥 BIGGER LABELS */
.custom-label {
    color: white;
    font-size: 22px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 10px;
}

/* 🔥 WHITE PREMIUM SELECT */
[data-testid="stSelectbox"] > div {
    background: #ffffff !important;
    border-radius: 10px !important;
    font-size: 17px !important;
    color: #111 !important;
    border: 1px solid #e5e7eb !important;
}

/* Dropdown */
[data-baseweb="select"] {
    background: #ffffff !important;
}
[data-baseweb="select"] div {
    background: #ffffff !important;
    color: #111 !important;
}

/* BUTTON */
[data-testid="stButton"] {
    display: flex;
    justify-content: center;
}

[data-testid="stButton"] button {
    background: #22c55e;
    color: white;
    border-radius: 12px;
    padding: 18px 80px;
    font-size: 20px;
    font-weight: 700;
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# ── MODEL ─────────────────────────────
@st.cache_resource
def load_model():
    return ChatGroq(groq_api_key=st.secrets["GROQ_API_KEY"],
                    model="llama-3.1-8b-instant")
llm = load_model()

# ── HEADER ─────────────────────────────
st.markdown("""
<div class="pgx-header">
    <div class="pgx-header-text">
        <h1>PrepGuideX AI</h1>
        <p class="pgx-caption">Prepare with your Guide</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LAYOUT ─────────────────────────────
col1, col2 = st.columns([1, 1.5], gap="large")

# LEFT
with col1:
    uploaded_file = st.file_uploader(
        "Drag & Drop File here\nLimit 200mb per file",
        type="pdf"
    )

# RIGHT
with col2:
    st.markdown('<div class="custom-label">Choose what you want</div>', unsafe_allow_html=True)

    option = st.selectbox(
        "",
        ["Summary", "Key Points", "Keywords", "Questions", "Ask Doubts"]
    )

    level = None
    if option in ["Summary", "Key Points", "Ask Doubts"]:
        st.markdown('<div class="custom-label">Select Explanation Level</div>', unsafe_allow_html=True)

        level = st.selectbox(
            "",
            ["Beginner", "Intermediate", "Expert"]
        )

    user_q = ""
    if option == "Ask Doubts":
        user_q = st.text_input("Ask your question")

    generate_clicked = st.button("Generate")

# ── LOGIC ─────────────────────────────
if generate_clicked:

    if uploaded_file is None:
        st.warning("⚠️ Insert a PDF File !")
        st.stop()

    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    text = text[:5000]

    style = ""
    if level == "Beginner":
        style = "Explain simply."
    elif level == "Intermediate":
        style = "Explain clearly."
    elif level == "Expert":
        style = "Explain technically."

    if option == "Summary":
        prompt = f"{style}\nSummarize:\n{text}"
    elif option == "Key Points":
        prompt = f"{style}\nKey points:\n{text}"
    elif option == "Keywords":
        prompt = f"Extract keywords:\n{text}"
    elif option == "Questions":
        prompt = f"Generate questions:\n{text}"
    elif option == "Ask Doubts":
        if not user_q:
            st.warning("⚠️ Enter question")
            st.stop()
        prompt = f"{style}\n{text}\nQuestion: {user_q}"

    progress = st.progress(0)

    with st.spinner("Extracting insights…"):
        progress.progress(30)
        response = llm.invoke(prompt)
        progress.progress(100)

    st.markdown("---")
    st.subheader(option)
    st.write(response.content)
