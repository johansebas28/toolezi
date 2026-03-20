from flask import Blueprint, request, render_template
from pdf2image import convert_from_path
from pdf2docx import Converter
from PIL import Image
from pypdf import PdfReader
import os, zipfile, uuid, subprocess

convert_bp = Blueprint("convert", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# PDF → IMG
@convert_bp.route("/pdf_to_img", methods=["POST"])
def pdf_to_img():
    file = request.files["pdf"]

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    images = convert_from_path(pdf_path, poppler_path=r"C:\poppler-25.12.0\Library\bin")

    filename = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, filename)

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for i, img in enumerate(images):
            img_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.png")
            img.save(img_path, "PNG")
            zipf.write(img_path, f"page_{i+1}.png")

    os.remove(pdf_path)

    return render_template("result.html", filename=filename)


# IMG → PDF
@convert_bp.route("/img_to_pdf", methods=["POST"])
def img_to_pdf():
    files = request.files.getlist("images")

    paths = []
    image_list = []

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        paths.append(path)

        img = Image.open(path).convert("RGB")
        image_list.append(img)

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    image_list[0].save(output_path, save_all=True, append_images=image_list[1:])

    # 🔥 BORRAR TODAS LAS IMÁGENES
    for path in paths:
        os.remove(path)

    return render_template("result.html", filename=filename)


# PDF → WORD
@convert_bp.route("/pdf_to_word", methods=["POST"])
def pdf_to_word():
    file = request.files.get("pdf")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
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


# WORD → PDF
@convert_bp.route("/word_to_pdf", methods=["POST"])
def word_to_pdf():
    file = request.files.get("file")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    subprocess.run([
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        OUTPUT_FOLDER,
        input_path,
    ], check=True)

    os.remove(input_path)

    output_name = file.filename.replace(".docx", ".pdf")

    return render_template("result.html", filename=output_name)