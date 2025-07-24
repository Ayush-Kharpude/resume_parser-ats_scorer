import fitz  # PyMuPDF
import re
from io import BytesIO

def extract_resume_data(resume_file):
    # Reset file pointer to beginning
    resume_file.seek(0)
    
    # Create a buffer so we can read it multiple times
    file_buffer = BytesIO(resume_file.read())

    doc = fitz.open(stream=file_buffer.getvalue(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Clean up LaTeX-style tags like \csuse{...}
    text = re.sub(r"\\csuse\s?\{[^}]+\}", "", text)
    text = text.encode('ascii', errors='ignore').decode()

    # Extract email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group() if email_match else "Not Found"

    # Extract phone number (10-digit)
    phone_match = re.search(r"\b\d{10}\b", text)
    phone = phone_match.group() if phone_match else "Not Found"

    # Extract name — first non-empty line with at least 2 words
    name = "Not Found"
    for line in text.split("\n"):
        line = line.strip()
        if len(line.split()) >= 2 and any(c.isalpha() for c in line):
            name = line
            break

    # Skill matching from known list
    known_skills = [
        "HTML", "CSS", "JavaScript", "Node.js", "Express.js", "MongoDB", "MySQL",
        "REST APIs", "Postman", "Figma", "phpMyAdmin", "Python", "C++", "Java",
        "React", "Git", "GitHub", "Docker", "XAMPP"
    ]

    found_skills = []
    for skill in known_skills:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found_skills.append(skill)

    return text, {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": list(set(found_skills))
    }
    