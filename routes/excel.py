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

    if not filename_secure.endswith((".xls", ".xlsx")):
        return render_template("result.html", error="Formato no válido")

    filename_secure = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
    file.save(input_path)

    try:
        # 🔥 convertir con LibreOffice
        subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            OUTPUT_FOLDER,
            input_path,
        ], check=True)

        # 🔥 nombre final
        output_name = os.path.basename(input_path).replace(".xlsx", ".pdf").replace(".xls", ".pdf")
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        os.remove(input_path)

        return render_template("result.html", filename=output_name)

    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return render_template("result.html", error="Error converting Excel to PDF")