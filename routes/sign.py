from flask import Blueprint, request, render_template
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os, uuid

sign_bp = Blueprint("sign", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


# =========================
# FIRMA AUTOMÁTICA (NO TOCAR)
# =========================
def create_signature_overlay(image_path, overlay_path):
    c = canvas.Canvas(overlay_path)


    x = 400
    y = 50

    width = 150
    height = 80

    c.drawImage(image_path, x, y, width=width, height=height, mask='auto')
    c.save()


@sign_bp.route("/sign_pdf", methods=["POST"])
def sign_pdf():
    pdf_file = request.files.get("pdf")
    image_file = request.files.get("image")

    if not pdf_file or not image_file:
        return render_template("result.html", error="Faltan archivos")

    pdf_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{pdf_file.filename}")
    image_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{image_file.filename}")

    pdf_file.save(pdf_path)
    image_file.save(image_path)

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        overlay_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
        create_signature_overlay(image_path, overlay_path)

        overlay_reader = PdfReader(overlay_path)

        for page in reader.pages:
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)


        os.remove(pdf_path)
        os.remove(image_path)
        os.remove(overlay_path)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        return render_template("result.html", error="Error al firmar PDF")


# =========================
# FIRMA MANUAL (PRO)
# =========================

@sign_bp.route("/sign_manual", methods=["POST"])
def sign_manual():

    file = request.files.get("pdf")
    signature = request.files.get("image")

    if not file or not signature:
        return render_template("result.html", error="Faltan archivos")

    pdf_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    sig_name = f"{uuid.uuid4()}_{secure_filename(signature.filename)}"

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    sig_path = os.path.join(UPLOAD_FOLDER, sig_name)

    file.save(pdf_path)
    signature.save(sig_path)

    return render_template(
        "sign_manual.html",
        preview_image="/static/img/logo.png",  # 🔥 luego lo mejoramos
        signature_preview="/" + sig_path.replace("\\", "/"),
        pdf_path=pdf_name,
        sig_path=sig_name
    )


@sign_bp.route("/apply_signature_manual", methods=["POST"])
def apply_signature_manual():

    x = float(request.form.get("x"))
    y = float(request.form.get("y"))
    width = float(request.form.get("width"))

    pdf_name = request.form.get("pdf_name")
    sig_name = request.form.get("sig_name")

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    sig_path = os.path.join(UPLOAD_FOLDER, sig_name)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    page = reader.pages[0]

    pdf_width = float(page.mediabox.width)
    pdf_height = float(page.mediabox.height)

    # 🔥 ESCALA (IMPORTANTE)
    scale_x = pdf_width / 600
    scale_y = pdf_height / 800

    x_real = x * scale_x
    y_real = pdf_height - (y * scale_y) - 100

    overlay_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")

    c = canvas.Canvas(overlay_path, pagesize=(pdf_width, pdf_height))
    c.drawImage(sig_path, x_real, y_real, width=150, mask='auto')
    c.save()

    overlay = PdfReader(overlay_path)
    page.merge_page(overlay.pages[0])

    writer.add_page(page)

    output_filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    # 🧹 limpiar
    os.remove(pdf_path)
    os.remove(sig_path)
    os.remove(overlay_path)

    return render_template("result.html", filename=output_filename)