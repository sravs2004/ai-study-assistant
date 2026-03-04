import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load structured syllabus
with open("cbse_10_syllabus_structured.json", "r", encoding="utf-8") as f:
    syllabus = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

chapter_texts = []
chapter_metadata = []

for subject, chapters in syllabus.items():
    for chapter, topics in chapters.items():
        combined_text = chapter + " " + " ".join(topics if isinstance(topics, list) else [])
        chapter_texts.append(combined_text)
        chapter_metadata.append({
            "subject": subject,
            "chapter": chapter
        })

# Generate embeddings
embeddings = model.encode(chapter_texts)

# Convert to numpy array
embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save index
faiss.write_index(index, "syllabus_index.faiss")

# Save metadata
with open("chapter_metadata.json", "w", encoding="utf-8") as f:
    json.dump(chapter_metadata, f, indent=4)

print("✅ Embedding index created successfully!")