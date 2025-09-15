import streamlit as st
import pdfplumber
import docx
import google.generativeai as genai
import json
import re
#set up your Gemini api key 
genai.configure(api_key="AIzaSyD95XuEcHRwF4lAWgn6oSx4FJVlIgPpfbs")

model = genai.GenerativeModel("gemini-1.5-flash")


# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Extract text from DOCX
def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Call Gemini AI to parse resume
def parse_resume_with_gemini(resume_text):
    prompt = f"""
    Behave you  are a resume parser. Extract the following details from the given resume text and return in JSON format:

    {{
      "name": "",
      "contact": {{
        "phone": "",
        "email": "",
        "linkedin": "",
        "github": "",
        "location": ""
      }},
      "objective": "",
      "education": [],
      "projects": [],
      "skills": {{
        "programming_languages": [],
        "web_technologies": [],
        "database_systems": [],
        "cloud_technologies": [],
        "operating_systems": [],
        "version_control": []
      }},
      "leadership": [],
      "professional_traits": [],
      "certifications": [],
      "languages": [],
      "interests": [],
      "hobbies": []
    }}

    Resume Text:
    {resume_text}
    """

    response = model.generate_content(prompt)
    try:
        resume_json = json.loads(response.text)
    except:
        # In case Gemini response has formatting issues
        cleaned_text = re.sub(r"```json|```", "", response.text).strip()
        resume_json = json.loads(cleaned_text)

    return resume_json


# STREAMLIT APP
st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="wide")
st.title("📄 AI Resume Parser (Gemini + Streamlit)")
st.write("Upload your resume (PDF/DOCX) and get structured JSON output.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    # Extract text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    st.subheader("📑 Extracted Resume Text")
    with st.expander("Show raw text"):
        st.text(resume_text[:3000])  # show first 3000 chars for preview

    # Parse with Gemini
    if st.button("Parse Resume with Gemini"):
        with st.spinner("Parsing resume with Gemini AI..."):
            resume_json = parse_resume_with_gemini(resume_text)

        st.subheader("✅ Parsed Resume JSON")
        st.json(resume_json)

        # Option to download JSON
        json_str = json.dumps(resume_json, indent=4)
        st.download_button(
            label="💾 Download JSON",
            file_name="resume.json",
            mime="application/json",
            data=json_str
        )
