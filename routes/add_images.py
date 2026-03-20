from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from PIL import Image
import os, uuid

add_images_bp = Blueprint("add_images", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@add_images_bp.route("/add_images_pdf", methods=["POST"])
def add_images_pdf():

    pdf_file = request.files.get("pdf")
    images = request.files.getlist("images")

    if not pdf_file or pdf_file.filename == "":
        return "No se subió PDF"

    if not images or images[0].filename == "":
        return "No se subieron imágenes"

    # 🔵 GUARDAR PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(pdf_path)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # 🔵 AGREGAR PDF ORIGINAL
    for page in reader.pages:
        writer.add_page(page)

    image_paths = []

    # 🔵 PROCESAR IMÁGENES
    for img_file in images:
        path = os.path.join(UPLOAD_FOLDER, img_file.filename)
        img_file.save(path)
        image_paths.append(path)

        img = Image.open(path).convert("RGB")

        temp_pdf = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
        img.save(temp_pdf)

        img_reader = PdfReader(temp_pdf)
        writer.add_page(img_reader.pages[0])

        os.remove(temp_pdf)

    # 🟢 GUARDAR RESULTADO
    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔴 LIMPIEZA
    os.remove(pdf_path)

    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    return render_template("result.html", filename=filename)