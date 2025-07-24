import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os
import pickle

# Load cleaned data
data = pd.read_csv("backend/data/cleaned_resume_dataset.csv")

# Split features and labels
X = data['text']
y = data['label']

# Vectorize text using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
X_vect = vectorizer.fit_transform(X)

# Train a Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_vect, y)

# Evaluate
y_pred = model.predict(X_vect)
print(classification_report(y, y_pred))

# Save model and vectorizer
os.makedirs("backend/models", exist_ok=True)
with open("backend/models/resume_classifier.pkl", "wb") as f:
    pickle.dump(model, f)
with open("backend/models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Model and vectorizer saved to backend/models/")
