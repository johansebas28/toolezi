from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
import os, uuid, subprocess

excel_bp = Blueprint("excel", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@excel_bp.route("/excel_to_pdf", methods=["POST"])
def excel_to_pdf():

    file = request.files.get("file")

    # 🔥 VALIDACIÓN 1: archivo existe
    if not file or file.filename == "":
        return render_template("result.html", error="No se subió ningún archivo")

    # 🔥 LIMPIAR NOMBRE
    filename_secure = secure_filename(file.filename)

    # 🔥 VALIDACIÓN 2: extensión correcta
    if not filename_secure.lower().endswith((".xls", ".xlsx")):
        return render_template("result.html", error="Formato no válido (solo Excel)")

    # 🔥 GUARDAR ARCHIVO
    input_filename = f"{uuid.uuid4()}_{filename_secure}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    try:
        # 🔥 CONVERSIÓN
        subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            OUTPUT_FOLDER,
            input_path,
        ], check=True)

        # 🔥 NOMBRE OUTPUT
        output_name = os.path.splitext(input_filename)[0] + ".pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        # 🔥 VALIDACIÓN: verificar que se creó
        if not os.path.exists(output_path):
            return render_template("result.html", error="No se pudo generar el PDF")

        return render_template("result.html", filename=output_name)

    except subprocess.CalledProcessError:
        return render_template("result.html", error="Error al convertir (LibreOffice falló)")

    except Exception as e:
        print("ERROR EXCEL:", e)
        return render_template("result.html", error="Error inesperado al procesar el archivo")

    finally:
        # 🔥 LIMPIEZA SIEMPRE
        if os.path.exists(input_path):
            os.remove(input_path)
            