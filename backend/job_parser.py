import pdfplumber

def extract_job_description(file):
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    else:
        return file.read().decode("utf-8")
