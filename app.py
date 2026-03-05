from flask import Flask, render_template, request
import os
from ai_engine import generate_summary, generate_quiz, generate_feedback, generate_study_links
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import datetime
import pytesseract
from PIL import Image

# Load embedding model

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index

index = faiss.read_index("syllabus_index.faiss")

# Load metadata

with open("chapter_metadata.json", "r", encoding="utf-8") as f:
    chapter_metadata = json.load(f)

app = Flask(**name**)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

quiz_global = []
subject_global = ""
chapter_global = ""

# ---------- Keyword Extraction ----------

def extract_keywords(text, top_k=5):

```
words = text.lower().split()

stop_words = {
    "the","is","in","and","of","to","a","for","on","with","as","by","an"
}

filtered = [w for w in words if w not in stop_words and len(w) > 4]

freq = {}

for w in filtered:
    freq[w] = freq.get(w,0) + 1

sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)

keywords = [w[0] for w in sorted_words[:top_k]]

return keywords
```

def save_score(score, subject, chapter):

```
data = {
    "score": score,
    "subject": subject,
    "chapter": chapter,
    "time": str(datetime.datetime.now())
}

file = "progress.json"

if os.path.exists(file):
    with open(file,"r") as f:
        records = json.load(f)
else:
    records = []

records.append(data)

with open(file,"w") as f:
    json.dump(records,f)
```

# ---------- Semantic Search ----------

def find_similar_chapters(text, top_k=3):

```
query_embedding = model.encode([text])
query_embedding = np.array(query_embedding).astype("float32")

distances, indices = index.search(query_embedding, top_k)

results = []

for i, idx in enumerate(indices[0]):

    distance = float(distances[0][i])
    confidence = round((1/(1+distance))*100,2)

    results.append({
        "subject": chapter_metadata[idx]["subject"],
        "chapter": chapter_metadata[idx]["chapter"],
        "score": distance,
        "confidence": confidence
    })

return results
```

@app.route("/")
def home():
return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

```
global quiz_global, subject_global, chapter_global

if "file" not in request.files:
    return "No file uploaded"

file = request.files["file"]

if file.filename == "":
    return "No selected file"

upload_folder = "static/uploads"
os.makedirs(upload_folder, exist_ok=True)

filepath = os.path.join(upload_folder, file.filename)
file.save(filepath)

# OCR
try:
    image = Image.open(filepath)
    extracted_text = pytesseract.image_to_string(image)

    if extracted_text.strip() == "":
        extracted_text = "No readable text detected in the image."

except Exception as e:
    extracted_text = f"OCR error: {str(e)}"

# Semantic detection
matches = find_similar_chapters(extracted_text)

if matches[0]["score"] > 2:
    return "Uploaded notes do not match CBSE Class 10 syllabus."

top_subject = matches[0]["subject"]
top_chapter = matches[0]["chapter"]

# Keywords
keywords = extract_keywords(extracted_text)

# AI Generation
summary = generate_summary(extracted_text, top_subject, top_chapter)

quiz_json = generate_quiz(extracted_text, top_subject, top_chapter)
quiz = json.loads(quiz_json)

quiz_global = quiz
subject_global = top_subject
chapter_global = top_chapter

return render_template(
    "result.html",
    filename=file.filename,
    text=extracted_text,
    matches=matches,
    top_subject=top_subject,
    top_chapter=top_chapter,
    summary=summary,
    quiz=quiz,
    keywords=keywords
)
```

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

```
global quiz_global, subject_global, chapter_global

user_answers = request.form

correct_count = 0
total_questions = len(quiz_global)

results = []

for i, q in enumerate(quiz_global):

    selected = user_answers.get(f"q{i}")
    correct_key = q["answer"]

    is_correct = selected == correct_key

    if is_correct:
        correct_count += 1

    results.append({
        "question": q["question"],
        "selected": selected,
        "correct": correct_key,
        "explanation": q["explanation"],
        "is_correct": is_correct
    })

score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0
save_score(score, subject_global, chapter_global)

feedback = generate_feedback(score, subject_global, chapter_global)

study_links = None

if correct_count < total_questions:
    study_links = generate_study_links(subject_global, chapter_global)

return render_template(
    "quiz_result.html",
    score=score,
    results=results,
    feedback=feedback,
    study_links=study_links
)
```

def find_weak_topics(records):

```
subject_scores = {}

for r in records:

    subject = r["subject"]
    score = r["score"]

    if subject not in subject_scores:
        subject_scores[subject] = []

    subject_scores[subject].append(score)

weak_topics = []

for subject, scores in subject_scores.items():

    avg = sum(scores) / len(scores)

    if avg < 60:
        weak_topics.append({
            "subject": subject,
            "average": round(avg,2)
        })

return weak_topics
```

@app.route("/dashboard")
def dashboard():

```
file = "progress.json"

if os.path.exists(file):
    with open(file,"r") as f:
        records = json.load(f)
else:
    records = []

scores = [r["score"] for r in records]
subjects = [r["subject"] for r in records]

weak_topics = find_weak_topics(records)

return render_template(
    "dashboard.html",
    scores=scores,
    subjects=subjects,
    records=records,
    weak_topics=weak_topics
)
```

if **name** == "**main**":

```
port = int(os.environ.get("PORT", 10000))

app.run(host="0.0.0.0", port=port, debug=False)
```
