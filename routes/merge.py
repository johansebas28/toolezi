from flask import Blueprint, request, render_template
from pypdf import PdfWriter, PdfReader
import os, uuid

merge_bp = Blueprint("merge", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@merge_bp.route("/merge", methods=["POST"])
def merge_pdf():
    files = request.files.getlist("pdfs")

    writer = PdfWriter()
    file_paths = []

    # 🟡 1. GUARDAR ARCHIVOS
    for file in files:
        if file.filename == "":
            continue

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        file_paths.append(path)

    # 🔵 2. LEER Y UNIR PDFs
    for path in file_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    # 🟢 3. CREAR OUTPUT
    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔴 4. BORRAR UPLOADS (AQUÍ ES CORRECTO)
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)

    return render_template("result.html", filename=filename)