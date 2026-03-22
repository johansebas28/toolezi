from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import os, uuid

number_bp = Blueprint("number", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


def create_number_overlay(page_width, page_height, page_number):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # 🔥 posición (puedes ajustar)
    c.setFont("Helvetica", 10)
    c.drawRightString(page_width - 40, 20, f"{page_number}")

    c.save()
    packet.seek(0)
    return PdfReader(packet)


@number_bp.route("/number_pdf", methods=["POST"])
def number_pdf():
    file = request.files.get("pdf")

    if not file:
        return render_template("result.html", error="No file provided")

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
    file.save(input_path)

    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for i, page in enumerate(reader.pages, start=1):
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            overlay_pdf = create_number_overlay(width, height, i)
            overlay_page = overlay_pdf.pages[0]

            # 🔥 fusionar número con la página
            page.merge_page(overlay_page)

            writer.add_page(page)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        os.remove(input_path)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        print("ERROR NUMBER:", e)

        if os.path.exists(input_path):
            os.remove(input_path)

        return render_template("result.html", error="Error numbering PDF")