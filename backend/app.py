import os
import pickle
import uvicorn
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and vectorizer
model_path = os.path.join(BASE_DIR, "models", "resume_classifier.pkl")
vectorizer_path = os.path.join(BASE_DIR, "models", "vectorizer.pkl")
label_map_path = os.path.join(BASE_DIR, "..", "data", "label_mapping.txt")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

label_map = {}
with open(label_map_path, "r") as f:
    for line in f:
        id_, label = line.strip().split(",")
        label_map[int(id_)] = label

class ResumeText(BaseModel):
    text: str

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

from utils.supabase_client import supabase  
@app.post("/predict/")
async def predict_resume(file: UploadFile = File(...)):
    contents = await file.read()
    temp_file_path = "temp_resume.pdf"
    
    with open(temp_file_path, "wb") as f:
        f.write(contents)

    resume_text = extract_text_from_pdf(temp_file_path)
    os.remove(temp_file_path)

    X = vectorizer.transform([resume_text])
    prediction = model.predict(X)[0]
    predicted_label = label_map[prediction]

    
    supabase.table("resumes").insert({
        "filename": file.filename,
        "predicted_label": predicted_label,
        "original_text": resume_text,
        "user_email": "test@example.com"  # later replace with actual email if using auth
    }).execute()

    return {"predicted_label": predicted_label}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
