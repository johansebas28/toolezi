from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
import os, uuid

rotate_bp = Blueprint("rotate", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@rotate_bp.route("/rotate_pdf", methods=["POST"])
def rotate_pdf():
    file = request.files.get("pdf")
    rotations = request.form.get("rotations")  # 🔥 AQUÍ LLEGA EL JSON

    if not file or file.filename == "":
        return "No se subió archivo"

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    # 🔥 convertir JSON a diccionario
    import json
    rotations_dict = json.loads(rotations) if rotations else {}

    # 🔵 ROTAR POR PÁGINA
    for i, page in enumerate(reader.pages):

        rotation = rotations_dict.get(str(i), 0)  # 👈 clave: index como string

        if rotation != 0:
            page.rotate(rotation)

        writer.add_page(page)

    # 🟢 CREAR OUTPUT
    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔴 BORRAR INPUT
    if os.path.exists(input_path):
        os.remove(input_path)

    return render_template("result.html", filename=filename)