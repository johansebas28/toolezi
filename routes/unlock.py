from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
import os, uuid

unlock_bp = Blueprint("unlock", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@unlock_bp.route("/unlock_pdf", methods=["POST"])
def unlock_pdf():

    # 🔹 Caso 1: viene archivo nuevo
    file = request.files.get("pdf")

    # 🔹 Caso 2: viene archivo temporal
    temp_name = request.form.get("temp_name")
    password = request.form.get("password")

    if file:
        filename_secure = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
        file.save(input_path)

    elif temp_name:
        input_path = os.path.join(UPLOAD_FOLDER, temp_name)

    else:
        return render_template("result.html", error="No file provided")

    try:
        reader = PdfReader(input_path)

        # 🔥 NO está protegido
        if not reader.is_encrypted:
            os.remove(input_path)
            return render_template("result.html", error="This PDF is not protected")

        # 🔥 intento sin contraseña (restricciones)
        if reader.decrypt("") != 0:
            return generate_unlocked(reader, input_path)

        # 🔐 necesita contraseña
        if not password:
            return render_template(
                "unlock_password.html",
                temp_name=os.path.basename(input_path)
            )

        # 🔐 intento con contraseña
        if reader.decrypt(password) == 0:
            return render_template(
                "unlock_password.html",
                temp_name=os.path.basename(input_path),
                error="Incorrect password"
            )

        return generate_unlocked(reader, input_path)

    except Exception:
        if os.path.exists(input_path):
            os.remove(input_path)
        return render_template("result.html", error="Error processing file")


def generate_unlocked(reader, input_path):
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    output_filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    os.remove(input_path)

    return render_template("result.html", filename=output_filename)