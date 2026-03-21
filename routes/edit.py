from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import os, uuid

edit_bp = Blueprint("edit", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


def create_text_overlay(text, overlay_path):
    c = canvas.Canvas(overlay_path)

    # 🔥 POSICIÓN (puedes mejorar luego)
    x = 100
    y = 500

    c.setFont("Helvetica", 16)
    c.drawString(x, y, text)

    c.save()


@edit_bp.route("/edit_pdf", methods=["POST"])
def edit_pdf():
    file = request.files.get("pdf")
    text = request.form.get("text")

    if not file or not text:
        return render_template("result.html", error="Faltan datos")

    pdf_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
    overlay_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")

    file.save(pdf_path)

    try:
        create_text_overlay(text, overlay_path)

        reader = PdfReader(pdf_path)
        overlay = PdfReader(overlay_path)

        writer = PdfWriter()

        for page in reader.pages:
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        os.remove(pdf_path)
        os.remove(overlay_path)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        return render_template("result.html", error="Error al editar PDF")