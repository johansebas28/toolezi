from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
import os, uuid

reorder_bp = Blueprint("reorder", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# 🔥 PREVIEW
@reorder_bp.route("/preview_reorder", methods=["POST"])
def preview_reorder():

    file = request.files["file"]

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    images = convert_from_path(
        pdf_path,
        poppler_path=r"C:\poppler-25.12.0\Library\bin"
    )

    image_paths = []

    for i, img in enumerate(images):
        img_name = f"{uuid.uuid4()}.png"
        img_path = os.path.join(OUTPUT_FOLDER, img_name)
        img.save(img_path, "PNG")

        image_paths.append({
            "src": f"/image/{img_name}",
            "page": i + 1
        })

    os.remove(pdf_path)

    return {"images": image_paths}


# 🔥 REORDER FINAL
@reorder_bp.route("/reorder_pdf", methods=["POST"])
def reorder_pdf():

    file = request.files.get("pdf")
    order = request.form.get("order")  # "3,1,2,4"

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    order_list = [int(x) for x in order.split(",")]

    for page_num in order_list:
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    os.remove(input_path)

    return render_template("result.html", filename=filename)