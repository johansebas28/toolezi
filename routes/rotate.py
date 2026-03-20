from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
import os, uuid

rotate_bp = Blueprint("rotate", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@rotate_bp.route("/rotate_pdf", methods=["POST"])
def rotate_pdf():
    file = request.files.get("pdf")
    rotation = int(request.form.get("rotation", 90))  # 90, 180, 270

    if not file or file.filename == "":
        return "No se subió archivo"

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    # 🔵 ROTAR TODAS LAS PÁGINAS
    for page in reader.pages:
        page.rotate(rotation)
        writer.add_page(page)

    # 🟢 CREAR OUTPUT
    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔴 BORRAR INPUT (AQUÍ VA)
    if os.path.exists(input_path):
        os.remove(input_path)

    return render_template("result.html", filename=filename)