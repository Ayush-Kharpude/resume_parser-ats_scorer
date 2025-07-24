# backend/preprocess_dataset.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os

# Load dataset
df = pd.read_csv("backend/resume_dataset/UpdatedResumeDataSet.csv")
df = df[['Resume', 'Category']].dropna()

# Label encode the categories
le = LabelEncoder()
df['label'] = le.fit_transform(df['Category'])

# Save cleaned dataset
os.makedirs("data", exist_ok=True)
df[['Resume', 'label']].rename(columns={'Resume': 'text'}).to_csv("data/cleaned_resume_dataset.csv", index=False)

# Save label mapping
with open("data/label_mapping.txt", "w") as f:
    for label, id in zip(le.classes_, le.transform(le.classes_)):
        f.write(f"{id},{label}\n")

print("✅ Cleaned data saved to: data/cleaned_resume_dataset.csv")
