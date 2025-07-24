import streamlit as st
import requests

st.set_page_config(page_title="Resume Classifier", page_icon="📄")

st.title("📄 Resume Classifier")
st.write("Upload your resume and get predicted job role")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    
    with st.spinner("Analyzing resume..."):
        response = requests.post("http://localhost:8000/predict/", files=files)

    if response.status_code == 200:
        result = response.json()
        st.success(f"✅ Predicted Job Role: **{result['predicted_label']}**")
    else:
        st.error("❌ Failed to classify resume.")
