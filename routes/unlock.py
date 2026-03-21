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

    file = request.files.get("pdf")
    temp_name = request.form.get("temp_name")
    password = request.form.get("password")

    input_path = None

    # 🔹 CASO 1: archivo nuevo
    if file:
        filename_secure = secure_filename(file.filename)
        temp_name = f"{uuid.uuid4()}_{filename_secure}"
        input_path = os.path.join(UPLOAD_FOLDER, temp_name)
        file.save(input_path)

    # 🔹 CASO 2: archivo temporal (ya subido antes)
    elif temp_name:
        input_path = os.path.join(UPLOAD_FOLDER, temp_name)

    else:
        return render_template("result.html", error="No file provided")

    try:
        reader = PdfReader(input_path)

        # 🔓 Si NO está protegido
        if not reader.is_encrypted:
            return generate_unlocked(reader, input_path)

        # 🔥 Intento automático (algunos PDFs permiten esto)
        if reader.decrypt("") != 0:
            return generate_unlocked(reader, input_path)

        # 🔐 NECESITA CONTRASEÑA → mostrar modal
        if not password:
            return render_template(
                "index.html",
                ask_password=True,
                temp_name=os.path.basename(input_path)
            )

        # 🔐 Intento con contraseña
        if reader.decrypt(password) == 0:
            return render_template(
                "index.html",
                ask_password=True,
                temp_name=os.path.basename(input_path),
                error="Contraseña incorrecta"
            )

        # 🔓 Desbloqueo exitoso
        return generate_unlocked(reader, input_path)

    except Exception as e:
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
        print("ERROR UNLOCK:", e)
        return render_template("result.html", error="Error processing file")


def generate_unlocked(reader, input_path):
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    output_filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🧹 borrar archivo original
    if os.path.exists(input_path):
        os.remove(input_path)

    return render_template("result.html", filename=output_filename)