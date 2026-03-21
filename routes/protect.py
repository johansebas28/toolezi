from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
import os, uuid

protect_bp = Blueprint("protect", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@protect_bp.route("/protect_pdf", methods=["POST"])
def protect_pdf():

    file = request.files.get("pdf")
    password = request.form.get("password")

    if not file or not password:
        return render_template("result.html", error="Falta archivo o contraseña")

    try:
        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # 🔐 PROTEGER PDF
        writer.encrypt(password)

        filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        os.remove(input_path)

        return render_template("result.html", filename=filename)

    except Exception as e:
        print("ERROR PROTECT:", e)
        return render_template("result.html", error="Error al proteger PDF")