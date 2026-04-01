from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
from pypdf import PdfWriter, PdfReader
import os, uuid

merge_bp = Blueprint("merge", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"


@merge_bp.route("/merge", methods=["POST"])
def merge_pdf():

    files = request.files.getlist("pdfs")

    # 🔥 VALIDACIÓN 1: que haya archivos
    if not files or all(f.filename == "" for f in files):
        return render_template("result.html", error="No se subieron archivos")

    writer = PdfWriter()
    file_paths = []

    try:
        # 🟡 1. GUARDAR SOLO PDFs
        for file in files:

            if file.filename == "":
                continue

            filename_secure = secure_filename(file.filename)

            # 🔥 VALIDACIÓN 2: solo PDFs
            if not filename_secure.lower().endswith(".pdf"):
                return render_template("result.html", error="Solo se permiten archivos PDF")

            path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
            file.save(path)
            file_paths.append(path)

        # 🔵 2. LEER Y UNIR
        for path in file_paths:
            try:
                reader = PdfReader(path)
            except Exception:
                return render_template("result.html", error="Uno de los archivos está dañado o no es un PDF válido")

            for page in reader.pages:
                writer.add_page(page)

        # 🟢 3. CREAR OUTPUT
        filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        return render_template("result.html", filename=filename)

    except Exception as e:
        print("MERGE ERROR:", e)
        return render_template("result.html", error="Error al unir los PDFs")

    finally:
        # 🔴 LIMPIEZA SIEMPRE
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)