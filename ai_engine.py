from groq import Groq
import json


import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def generate_summary(text, subject, chapter):
    prompt = f"""
Summarize the following CBSE Class 10 notes clearly and briefly.

Subject: {subject}
Chapter: {chapter}

Text:
{text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_quiz(text, subject, chapter):
    prompt = f"""
Generate 8 to 10 CBSE Class 10 MCQs.

Return ONLY valid JSON.

Format strictly:

[
  {{
    "question": "Question text",
    "options": [
      {{"key": "A", "text": "Option 1"}},
      {{"key": "B", "text": "Option 2"}},
      {{"key": "C", "text": "Option 3"}},
      {{"key": "D", "text": "Option 4"}}
    ],
    "answer": "Correct Option Key (A/B/C/D)",
    "explanation": "Why this is correct"
  }}
]

Subject: {subject}
Chapter: {chapter}

Text:
{text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_feedback(score, subject, chapter):
    prompt = f"""
A student scored {score}% in {subject} - {chapter}.

Provide strengths, weaknesses, and improvement strategy.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_study_links(subject, chapter):

    base_query = f"CBSE Class 10 {subject} {chapter}"

    youtube_link = (
        "https://www.youtube.com/results?search_query="
        + base_query.replace(" ", "+")
    )

    google_link = (
        "https://www.google.com/search?q="
        + base_query.replace(" ", "+")
    )

    ncert_link = "https://ncert.nic.in/textbook.php"

    return [
        ncert_link,
        youtube_link,
        google_link
    ]