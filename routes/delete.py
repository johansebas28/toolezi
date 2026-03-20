from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
import os, uuid

delete_bp = Blueprint("delete", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@delete_bp.route("/delete_pages", methods=["POST"])
def delete_pages():
    file = request.files.get("pdf")
    pages_str = request.form.get("pages")

    # 🔥 VALIDACIONES
    if not file or file.filename == "":
        return "No se subió archivo"

    if not pages_str:
        return "Debes seleccionar al menos una página"

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    try:
        pages_to_delete = set(int(p) for p in pages_str.split(","))
    except:
        os.remove(input_path)
        return "Error en páginas seleccionadas"

    # 🔥 ELIMINAR PÁGINAS
    for i, page in enumerate(reader.pages, start=1):
        if i not in pages_to_delete:
            writer.add_page(page)

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔥 BORRAR UPLOAD
    if os.path.exists(input_path):
        os.remove(input_path)

    return render_template("result.html", filename=filename)