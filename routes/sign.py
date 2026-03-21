from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import os, uuid

sign_bp = Blueprint("sign", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


def create_signature_overlay(image_path, overlay_path):
    c = canvas.Canvas(overlay_path)

    # 🔥 POSICIÓN (ajústala luego si quieres)
    x = 400
    y = 50

    width = 150
    height = 80

    c.drawImage(image_path, x, y, width=width, height=height, mask='auto')
    c.save()


@sign_bp.route("/sign_pdf", methods=["POST"])
def sign_pdf():
    pdf_file = request.files.get("pdf")
    image_file = request.files.get("image")

    if not pdf_file or not image_file:
        return render_template("result.html", error="Faltan archivos")

    pdf_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{pdf_file.filename}")
    image_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{image_file.filename}")

    pdf_file.save(pdf_path)
    image_file.save(image_path)

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        overlay_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
        create_signature_overlay(image_path, overlay_path)

        overlay_reader = PdfReader(overlay_path)

        for page in reader.pages:
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        # limpiar
        os.remove(pdf_path)
        os.remove(image_path)
        os.remove(overlay_path)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        return render_template("result.html", error="Error al firmar PDF")