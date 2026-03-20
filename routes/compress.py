from flask import Blueprint, request, render_template
import os, subprocess, uuid

compress_bp = Blueprint("compress", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@compress_bp.route("/compress_pdf", methods=["POST"])
def compress_pdf():
    file = request.files.get("pdf")
    quality = request.form.get("quality", "medium")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    quality_map = {
        "low": "/screen",
        "medium": "/ebook",
        "high": "/printer"
    }

    gs_quality = quality_map.get(quality, "/ebook")

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

    os.remove(input_path)

    original_size = round(os.path.getsize(input_path) / (1024 * 1024), 2) if os.path.exists(input_path) else 0
    compressed_size = round(os.path.getsize(output_path) / (1024 * 1024), 2)

    reduction = round(100 - (compressed_size / original_size * 100), 1) if original_size else 0

    return render_template(
        "result.html",
        filename=filename,
        original_size=original_size,
        compressed_size=compressed_size,
        reduction=reduction
    )