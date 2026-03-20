from flask import Blueprint, request, render_template
from pdf2image import convert_from_path
from pdf2docx import Converter
from PIL import Image
from pypdf import PdfReader
from werkzeug.utils import secure_filename

import os, zipfile, uuid, subprocess

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
ALLOWED_PDF = {"pdf"}
ALLOWED_IMAGES = {"png", "jpg", "jpeg"}
ALLOWED_WORD = {"docx"}

convert_bp = Blueprint("convert", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

# PDF TO IMG
@convert_bp.route("/pdf_to_img", methods=["POST"])
def pdf_to_img():
    file = request.files["pdf"]

    if not allowed_file(file.filename, ALLOWED_PDF):
        return render_template("result.html", error="Solo se permiten archivos PDF")
    
    filename_secure = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
    file.save(pdf_path)

    images = convert_from_path(pdf_path)

    zip_name = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, zip_name)

    temp_images = []

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for i, img in enumerate(images):
            img_name = f"{uuid.uuid4()}.png"
            img_path = os.path.join(OUTPUT_FOLDER, img_name)
            img.save(img_path, "PNG")
            zipf.write(img_path, f"page_{i+1}.png")
            temp_images.append(img_path)

    # 🔥 limpiar temporales
    os.remove(pdf_path)
    for img in temp_images:
        os.remove(img)

    return render_template("result.html", filename=zip_name)

# IMG TO PDF
@convert_bp.route("/img_to_pdf", methods=["POST"])
def img_to_pdf():
    files = request.files.getlist("images")
    
    paths = []
    image_list = []

    for file in files:
        if not allowed_file(file.filename, ALLOWED_IMAGES):
            return render_template("result.html", error="Solo imágenes JPG o PNG")
        filename_secure = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
        file.save(path)
        paths.append(path)

        img = Image.open(path).convert("RGB")
        image_list.append(img)

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    image_list[0].save(output_path, save_all=True, append_images=image_list[1:])

    for path in paths:
        os.remove(path)

    return render_template("result.html", filename=filename)

# PDF TO WORD
@convert_bp.route("/pdf_to_word", methods=["POST"])
def pdf_to_word():
    file = request.files.get("pdf")

    if not allowed_file(file.filename, ALLOWED_PDF):
        return render_template("result.html", error="Solo se permiten archivos PDF")

    filename_secure = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
    file.save(input_path)

    reader = PdfReader(input_path)

    if len(reader.pages) > 50:
        os.remove(input_path)
        return render_template("result.html", filename=None, error="Máximo 50 páginas")

    filename = f"{uuid.uuid4()}.docx"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

    os.remove(input_path)

    return render_template("result.html", filename=filename)

# WORD TO PDF
@convert_bp.route("/word_to_pdf", methods=["POST"])
def word_to_pdf():
    file = request.files.get("file")

    if not allowed_file(file.filename, ALLOWED_WORD):
        return render_template("result.html", error="Solo archivos Word (.docx)")
    
    filename_secure = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
    file.save(input_path)

    subprocess.run(
        [
            "soffice",  # 🔥 esto funciona en Render/Linux
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            OUTPUT_FOLDER,
            input_path,
        ],
        check=True,
    )

    output_name = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"

    os.remove(input_path)

    return render_template("result.html", filename=output_name)
