from flask import Flask, render_template, request, send_file
import os
from quiz_logic import generate_quiz_from_pdf, save_to_json, save_to_pdf

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    pdf = request.files["pdf"]
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(pdf_path)

    quiz_data = generate_quiz_from_pdf(pdf_path)

    save_to_json(quiz_data, os.path.join(OUTPUT_FOLDER, "quiz.json"))
    save_to_pdf(quiz_data, os.path.join(OUTPUT_FOLDER, "quiz.pdf"))

    return render_template("index.html", success=True)


@app.route("/download/json")
def download_json():
    return send_file("outputs/quiz.json", as_attachment=True)


@app.route("/download/pdf")
def download_pdf():
    return send_file("outputs/quiz.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
