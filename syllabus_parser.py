import pdfplumber
import json
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_syllabus(text):
    chapters = {}
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # Basic logic: detect chapter headings
        if line.isupper() and len(line) > 5:
            chapters[line] = []

        elif len(chapters) > 0:
            last_chapter = list(chapters.keys())[-1]
            chapters[last_chapter].append(line)

    return chapters

def process_all_pdfs(folder_path):
    syllabus_data = {}

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            subject_name = file.replace(".pdf", "").capitalize()
            pdf_path = os.path.join(folder_path, file)

            text = extract_text_from_pdf(pdf_path)
            parsed = parse_syllabus(text)

            syllabus_data[subject_name] = parsed

    return syllabus_data

if __name__ == "__main__":
    folder = "cbse_syllabus_raw"
    full_syllabus = process_all_pdfs(folder)

    with open("cbse_10_syllabus.json", "w") as f:
        json.dump(full_syllabus, f, indent=4)

    print("Syllabus JSON generated successfully!")