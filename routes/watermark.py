from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os, uuid

watermark_bp = Blueprint("watermark", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


def create_watermark(text, path):
    c = canvas.Canvas(path, pagesize=letter)

    c.setFont("Helvetica", 40)
    c.setFillGray(0.5, 0.3)  # gris + transparencia

    c.saveState()
    c.translate(300, 400)
    c.rotate(45)

    c.drawCentredString(0, 0, text)
    c.restoreState()

    c.save()


@watermark_bp.route("/watermark_pdf", methods=["POST"])
def watermark_pdf():

    file = request.files.get("pdf")
    text = request.form.get("text")

    if not file or not text:
        return render_template("result.html", error="Falta archivo o texto")

    try:
        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
        watermark_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_wm.pdf")

        file.save(input_path)

        # Crear marca de agua
        create_watermark(text, watermark_path)

        reader = PdfReader(input_path)
        watermark = PdfReader(watermark_path)

        writer = PdfWriter()

        for page in reader.pages:
            page.merge_page(watermark.pages[0])
            writer.add_page(page)

        filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        # limpiar
        os.remove(input_path)
        os.remove(watermark_path)

        return render_template("result.html", filename=filename)

    except Exception as e:
        print("ERROR WATERMARK:", e)
        return render_template("result.html", error="Error al aplicar marca de agua")