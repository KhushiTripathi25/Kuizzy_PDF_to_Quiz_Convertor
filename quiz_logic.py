import pdfplumber
import nltk
import re
import random
import json

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# -----------------------------
# NLTK setup (run once)
# -----------------------------
nltk.download("punkt")
nltk.download("stopwords")


# -----------------------------
# STEP 1: Extract text from PDF
# -----------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text


# -----------------------------
# STEP 2: Clean text
# -----------------------------
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^A-Za-z0-9., ]", "", text)
    return text.strip()


# -----------------------------
# STEP 3: Important sentence extraction
# -----------------------------
def get_important_sentences(text):
    sentences = sent_tokenize(text)
    keywords = ["is", "are", "defined", "refers", "consists"]

    important = [
        s for s in sentences
        if any(k in s.lower() for k in keywords) and len(s.split()) > 6
    ]
    return important


# -----------------------------
# STEP 4: Keyword extraction
# -----------------------------
def extract_keywords(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())

    return list({
        w for w in words
        if w.isalpha() and w not in stop_words
    })


# -----------------------------
# STEP 5A: Fill in the blanks
# -----------------------------
def generate_fill_blanks(sentence):
    words = sentence.split()
    if len(words) < 8:
        return None

    index = len(words) // 2
    answer = words[index]
    question = sentence.replace(answer, "_____")

    return question, answer


# -----------------------------
# STEP 5B: True / False
# -----------------------------
def generate_true_false(sentence):
    return sentence, "True"


# -----------------------------
# STEP 5C: MCQ generation
# -----------------------------
def generate_mcq(sentence, keywords):
    if len(keywords) < 4:
        return None

    correct = random.choice(keywords)
    options = random.sample(keywords, 3) + [correct]
    random.shuffle(options)

    question = f"Which of the following best relates to: {sentence}"
    return question, options, correct


# -----------------------------
# STEP 6: Save to JSON
# -----------------------------
def save_to_json(quiz_data, filename="quiz_output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, indent=4)


# -----------------------------
# STEP 7: Save to PDF
# -----------------------------
def save_to_pdf(quiz_data, filename="quiz_output.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    x, y = 40, height - 50
    c.setFont("Helvetica", 11)
    c.drawString(x, y, "Generated Quiz")
    y -= 30

    for i, q in enumerate(quiz_data, start=1):
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50

        c.drawString(x, y, f"{i}. ({q['type']}) {q['question']}")
        y -= 20

        if q["type"] == "MCQ":
            for opt in q["options"]:
                c.drawString(x + 20, y, f"- {opt}")
                y -= 15

        c.drawString(x + 20, y, f"Answer: {q['answer']}")
        y -= 30

    c.save()


# -----------------------------
# STEP 8: Core quiz generator
# -----------------------------
def generate_quiz_from_pdf(pdf_path, limit=5):
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)

    important_sentences = get_important_sentences(cleaned_text)
    keywords = extract_keywords(cleaned_text)

    quiz = []

    for sentence in important_sentences[:limit]:
        fb = generate_fill_blanks(sentence)
        if fb:
            quiz.append({
                "type": "Fill in the Blanks",
                "question": fb[0],
                "answer": fb[1]
            })

        tf_q, tf_a = generate_true_false(sentence)
        quiz.append({
            "type": "True/False",
            "question": tf_q,
            "answer": tf_a
        })

        mcq = generate_mcq(sentence, keywords)
        if mcq:
            quiz.append({
                "type": "MCQ",
                "question": mcq[0],
                "options": mcq[1],
                "answer": mcq[2]
            })

    return quiz


# -----------------------------
# STEP 9: Entry point
# -----------------------------
if __name__ == "__main__":
    pdf_path = "input.pdf"

    quiz_data = generate_quiz_from_pdf(pdf_path)

    save_to_json(quiz_data)
    save_to_pdf(quiz_data)

    print("Quiz generated successfully (JSON + PDF)")
