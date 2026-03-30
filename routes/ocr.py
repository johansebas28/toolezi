from flask import Blueprint, request, render_template
from pdf2image import convert_from_path
import pytesseract
from pytesseract import image_to_pdf_or_hocr
from PIL import Image
import os, uuid

# 🔥 CONFIGURACIÓN TESSERACT (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ocr_bp = Blueprint("ocr", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@ocr_bp.route("/ocr_pdf", methods=["POST"])
def ocr_pdf():
    file = request.files.get("file")

    if not file:
        return render_template("result.html", error="No file provided")

    filename = file.filename.lower()

    # 🔥 guardar archivo
    ext = os.path.splitext(filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}{ext}")
    file.save(input_path)

    try:
        # =========================
        # 📄 CONVERTIR A IMÁGENES
        # =========================
        if filename.endswith(".pdf"):
            images = convert_from_path(input_path, dpi=300)  # 🔥 más calidad
        else:
            images = [Image.open(input_path)]

        # =========================
        # 🔍 OCR → PDF REAL
        # =========================
        pdf_bytes = b""

        for img in images:

            # 🔥 mejorar imagen (sin destruirla)
            img = img.convert("L")

            # 🔥 OCR → PDF con texto invisible
            pdf_page = image_to_pdf_or_hocr(
                img,
                extension='pdf',
                lang='eng',
                config='--oem 3 --psm 6'
            )

            pdf_bytes += pdf_page

        # =========================
        # 💾 GUARDAR RESULTADO
        # =========================
        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        # =========================
        # 🧹 LIMPIEZA
        # =========================
        if os.path.exists(input_path):
            os.remove(input_path)

        print("OCR OK:", output_filename)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        print("OCR ERROR:", e)

        if os.path.exists(input_path):
            os.remove(input_path)

        return render_template("result.html", error="Error processing OCR")