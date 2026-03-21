from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
import os, uuid, subprocess

ppt_bp = Blueprint("ppt", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@ppt_bp.route("/ppt_to_pdf", methods=["POST"])
def ppt_to_pdf():

    file = request.files.get("file")

    if not file:
        return render_template("result.html", error="No file provided")

    filename_secure = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename_secure}")
    file.save(input_path)

    try:
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
        output_name = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"

        os.remove(input_path)

        return render_template("result.html", filename=output_name)

    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return render_template("result.html", error="Error converting PowerPoint to PDF")