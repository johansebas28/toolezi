from flask import Blueprint, request, render_template
from pdf2image import convert_from_path
import pytesseract
from reportlab.pdfgen import canvas
from PIL import Image
import os, uuid

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

    # 🔥 guardar archivo con extensión correcta
    ext = os.path.splitext(filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}{ext}")
    file.save(input_path)

    try:
        # 🔥 detectar tipo de archivo
        if filename.endswith(".pdf"):
            images = convert_from_path(input_path)
        else:
            images = [Image.open(input_path)]

        # 🔥 crear PDF de salida
        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        c = canvas.Canvas(output_path)

        for img in images:
            # mejorar imagen
            img = img.rotate(90, expand=True)  # si viene rotado
            img = img.convert("L")
            img = img.point(lambda x: 0 if x < 140 else 255)  # binarización

            # OCR
            custom_config = r'--oem 3 --psm 4'

            text = pytesseract.image_to_string(
                img,
                lang="spa+eng",
                config=custom_config
            )

            lines = text.split("\n")

            y = 800
            for line in lines:
                if line.strip():  # evita líneas vacías
                    c.drawString(40, y, line)
                    y -= 14

            c.showPage()

        c.save()

        # limpiar archivo subido
        if os.path.exists(input_path):
            os.remove(input_path)
        print("OUTPUT:", output_filename)
        return render_template("result.html", filename=output_filename)

    except Exception as e:
        print("OCR ERROR:", e)

        if os.path.exists(input_path):
            os.remove(input_path)

        return render_template("result.html", error="Error processing OCR")