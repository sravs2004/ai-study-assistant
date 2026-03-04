import json
import re
from groq import Groq

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("cbse_10_syllabus.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

structured_data = {}

def clean_json_response(text):
    # Remove markdown if present
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

for subject, content in raw_data.items():

    print(f"\nProcessing {subject}...")

    structured_data[subject] = {}

    # Convert subject content to string
    subject_text = json.dumps(content)

    # Split into smaller chunks (3000 characters each)
    chunks = [subject_text[i:i+3000] for i in range(0, len(subject_text), 3000)]

    chapter_counter = 1

    for chunk in chunks:

        print(f"  Processing chunk {chapter_counter}...")

        prompt = f"""
You are an expert syllabus data structuring AI.

Convert the following CBSE Class 10 syllabus text
into clean structured JSON.

Rules:
- Output ONLY valid JSON
- No explanations
- No markdown
- Format: Chapter → Subtopics
- Remove marks and instructions

Text:
{chunk}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )

        cleaned_text = clean_json_response(
            response.choices[0].message.content
        )

        try:
            parsed_chunk = json.loads(cleaned_text)
            structured_data[subject].update(parsed_chunk)
        except Exception as e:
            print(f"    ⚠ JSON parse failed for chunk {chapter_counter}")
            print("    Skipping this chunk...")

        chapter_counter += 1

with open("cbse_10_syllabus_structured.json", "w", encoding="utf-8") as f:
    json.dump(structured_data, f, indent=4)

print("\n✅ Fully Structured Syllabus Generated!")