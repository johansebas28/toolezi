from flask import Blueprint, request, render_template, jsonify
from werkzeug.utils import secure_filename
from pypdf import PdfWriter, PdfReader
from pdf2image import convert_from_path
import os, uuid
import threading
import time

split_bp = Blueprint("split", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# 🔥 asegurarse que existan las carpetas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MAX_PREVIEW = 15


# =========================
# 🔥 LIMPIEZA AUTOMÁTICA
# =========================
def delete_temp_images(paths):
    time.sleep(60)  # espera 1 minuto
    for path in paths:
        try:
            full_path = os.path.join(OUTPUT_FOLDER, os.path.basename(path))
            if os.path.exists(full_path):
                os.remove(full_path)
        except:
            pass


# =========================
# SPLIT REAL
# =========================
@split_bp.route("/split", methods=["POST"])
def split_pdf():

    file = request.files.get("pdf")
    pages_str = request.form.get("pages")

    if not file or file.filename == "":
        return render_template("result.html", error="No se subió ningún archivo")

    if not pages_str:
        return render_template("result.html", error="Debes seleccionar páginas")

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

        # 🔥 PARSEO SEGURO
        for part in pages_str.split(","):
            part = part.strip()

            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    for i in range(start, end + 1):
                        pages.add(i)
                except:
                    continue
            else:
                try:
                    pages.add(int(part))
                except:
                    continue

        if not pages:
            return render_template("result.html", error="Páginas inválidas")

        total_pages = len(reader.pages)

        valid_pages = [p for p in pages if 1 <= p <= total_pages]

        if not valid_pages:
            return render_template("result.html", error="Páginas fuera de rango")

        for page_num in sorted(valid_pages):
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
            last_page=MAX_PREVIEW
        )

        image_paths = []

        for img in images:
            img_name = f"{uuid.uuid4()}.png"
            img_path = os.path.join(OUTPUT_FOLDER, img_name)
            img.save(img_path, "PNG")
            image_paths.append(f"/image/{img_name}")

        # 🔥 LIMPIEZA AUTOMÁTICA EN SEGUNDO PLANO
        threading.Thread(target=delete_temp_images, args=(image_paths,)).start()

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