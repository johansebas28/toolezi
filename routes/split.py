from flask import Blueprint, request, render_template, jsonify
from werkzeug.utils import secure_filename
from pypdf import PdfWriter, PdfReader
from pdf2image import convert_from_path
import os, uuid

split_bp = Blueprint("split", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

MAX_PREVIEW = 15


# =========================
# SPLIT REAL
# =========================
@split_bp.route("/split", methods=["POST"])
def split_pdf():

    file = request.files.get("pdf")
    pages_str = request.form.get("pages")

    # 🔥 VALIDACIÓN
    if not file or file.filename == "":
        return render_template("result.html", error="No se subió ningún archivo")

    filename_secure = secure_filename(file.filename)

    if not filename_secure.lower().endswith(".pdf"):
        return render_template("result.html", error="Solo se permiten archivos PDF")

    input_filename = f"{uuid.uuid4()}_{filename_secure}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    try:
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

        return render_template("result.html", filename=filename)

    except Exception as e:
        print("SPLIT ERROR:", e)
        return render_template("result.html", error="Error al dividir el PDF")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)


# =========================
# PREVIEW INTELIGENTE
# =========================
@split_bp.route("/preview_pages", methods=["POST"])
def preview_pages():

    file = request.files.get("file")

    if not file or file.filename == "":
        return jsonify({"error": "No se envió archivo"}), 400

    filename_secure = secure_filename(file.filename)

    # 🔥 VALIDACIÓN CLAVE
    if not filename_secure.lower().endswith(".pdf"):
        return jsonify({"error": "Solo se permiten archivos PDF"}), 400

    pdf_filename = f"{uuid.uuid4()}_{filename_secure}"
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    file.save(pdf_path)

    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        # 🔴 MODO SIMPLE
        if total_pages > MAX_PREVIEW:
            return jsonify({
                "mode": "simple",
                "total_pages": total_pages
            })

        # 🟢 PREVIEW
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

        return jsonify({
            "mode": "preview",
            "images": image_paths
        })

    except Exception as e:
        print("PREVIEW ERROR:", e)
        return jsonify({"error": "Archivo inválido o dañado"}), 400

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)