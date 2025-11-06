import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document
from PyPDF2 import PdfReader
import json
from openai import OpenAI

# ---- PAGE SETUP ----
st.set_page_config(page_title="Resume Checker", page_icon="📄")
st.title("📄 Resume Checker using OpenAI")

# ---- API KEY INPUT ----
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
if not api_key:
    st.info("Please enter your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# ---- FILE UPLOADS ----
st.subheader("Upload Files")
jd_file = st.file_uploader("📄 Upload Job Description (PDF only)", type=["pdf"])
resume_file = st.file_uploader("👤 Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

# ---- PROCESS FILES ----
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join(p.text for p in doc.paragraphs)

# ---- ANALYZE ----
if jd_file and resume_file:
    job_description_text = extract_text_from_pdf(jd_file)
    resume_text = ""
    if resume_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = extract_text_from_docx(resume_file)

    st.success("✅ Files uploaded successfully!")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing with OpenAI..."):
            prompt = f"""
            You are a professional HR assistant.
            Job Description:
            {job_description_text}

            Resume:
            {resume_text}

            Tasks:
            1. Score the resume out of 10 based on job fit.
            2. Extract applicant details: Name, Email, Phone, Skills, Education, Experience.
            3. Provide a short feedback (2-3 lines).
            Return only valid JSON, no explanations.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            st.subheader("📊 Resume Evaluation Result")
            st.json(result_json)

            # ---- SAVE TO EXCEL ----
            df = pd.DataFrame([result_json])
            df.to_excel("resume_analysis.xlsx", index=False)

            with open("resume_analysis.xlsx", "rb") as f:
                st.download_button("⬇️ Download Excel Results", f, file_name="resume_analysis.xlsx")
