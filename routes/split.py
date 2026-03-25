from flask import Blueprint, request, render_template
from pypdf import PdfWriter, PdfReader
from pdf2image import convert_from_path
import os, uuid

split_bp = Blueprint("split", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# 🔥 límite de preview
MAX_PREVIEW = 15


@split_bp.route("/split", methods=["POST"])
def split_pdf():
    file = request.files.get("pdf")
    pages_str = request.form.get("pages")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    pages = set()
    for part in pages_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            for i in range(int(start), int(end) + 1):
                pages.add(i)
        else:
            pages.add(int(part))

    for page_num in sorted(pages):
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🔥 BORRAR INPUT
    if os.path.exists(input_path):
        os.remove(input_path)

    return render_template("result.html", filename=filename)


# 🔥 PREVIEW INTELIGENTE
@split_bp.route("/preview_pages", methods=["POST"])
def preview_pages():
    file = request.files["file"]

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # 🔴 MODO SIMPLE (PDF grande)
    if total_pages > MAX_PREVIEW:
        os.remove(pdf_path)
        return {
            "mode": "simple",
            "total_pages": total_pages
        }

    # 🟢 MODO PREVIEW (PDF pequeño)
    images = convert_from_path(
        pdf_path,
        first_page=1,
        last_page=MAX_PREVIEW,
        poppler_path=r"C:\poppler-25.12.0\Library\bin"
    )

    image_paths = []

    for img in images:
        img_name = f"{uuid.uuid4()}.png"
        img_path = os.path.join(OUTPUT_FOLDER, img_name)
        img.save(img_path, "PNG")
        image_paths.append(f"/image/{img_name}")

    # 🔥 BORRAR PDF ORIGINAL
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return {
        "mode": "preview",
        "images": image_paths
    }