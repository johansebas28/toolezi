from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
import os, subprocess, uuid

compress_bp = Blueprint("compress", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"


@compress_bp.route("/compress_pdf", methods=["POST"])
def compress_pdf():

    file = request.files.get("pdf")
    quality = request.form.get("quality", "medium")

    # 🔥 VALIDACIÓN 1: archivo existe
    if not file or file.filename == "":
        return render_template("result.html", error="No se subió ningún archivo")

    filename_secure = secure_filename(file.filename)

    # 🔥 VALIDACIÓN 2: solo PDF
    if not filename_secure.lower().endswith(".pdf"):
        return render_template("result.html", error="Solo se permiten archivos PDF")

    input_filename = f"{uuid.uuid4()}_{filename_secure}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    output_filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    quality_map = {
        "low": "/screen",
        "medium": "/ebook",
        "high": "/printer"
    }

    gs_quality = quality_map.get(quality, "/ebook")

    try:
        subprocess.run([
            r"C:\Program Files\gs\gs10.07.0\bin\gswin64c.exe",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path,
        ], check=True)

        # 🔥 VALIDAR QUE SE CREÓ
        if not os.path.exists(output_path):
            return render_template("result.html", error="No se pudo comprimir el PDF")

        original_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)
        compressed_size = round(os.path.getsize(output_path) / (1024 * 1024), 2)

        reduction = round(100 - (compressed_size / original_size * 100), 1) if original_size else 0

        return render_template(
            "result.html",
            filename=output_filename,
            original_size=original_size,
            compressed_size=compressed_size,
            reduction=reduction
        )

    except subprocess.CalledProcessError:
        return render_template("result.html", error="Error al comprimir el PDF (Ghostscript falló)")

    except Exception as e:
        print("COMPRESS ERROR:", e)
        return render_template("result.html", error="Error inesperado al procesar el archivo")

    finally:
        # 🔥 LIMPIEZA SIEMPRE
        if os.path.exists(input_path):
            os.remove(input_path)