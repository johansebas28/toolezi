from flask import Blueprint, request, render_template, url_for
from werkzeug.utils import secure_filename
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

import os
import uuid
import fitz  # 🔥 PyMuPDF

# 🔥 Blueprint
sign_manual_bp = Blueprint("sign_manual", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


# =========================
# 🖊️ VISTA MANUAL
# =========================
@sign_manual_bp.route("/sign_manual", methods=["POST"])
def sign_manual():

    file = request.files.get("pdf")
    signature = request.files.get("image")

    if not file or not signature:
        return render_template("result.html", error="Faltan archivos")

    # 🔥 nombres únicos
    pdf_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    sig_name = f"{uuid.uuid4()}_{secure_filename(signature.filename)}"

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    sig_path = os.path.join(UPLOAD_FOLDER, sig_name)

    # 🔥 guardar archivos
    file.save(pdf_path)
    signature.save(sig_path)

    print("PDF GUARDADO:", pdf_path)
    print("FIRMA GUARDADA:", sig_path)

    # 🔥 GENERAR PREVIEW CON PyMuPDF (SIN POPPLER)
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]

        pix = page.get_pixmap()

        preview_name = f"{uuid.uuid4()}.png"
        preview_path = os.path.join(UPLOAD_FOLDER, preview_name)

        pix.save(preview_path)

        print("PREVIEW CREADO:", preview_path)

    except Exception as e:
        print("ERROR PREVIEW:", e)
        return render_template("result.html", error="Error generando preview")


    return render_template(
        "sign_manual.html",
        preview_image=url_for("serve_image", filename=preview_name),
        signature_preview=url_for("serve_image", filename=sig_name),
        pdf_path=pdf_name,
        sig_path=sig_name
    )


# =========================
# 🧩 APLICAR FIRMA
# =========================
@sign_manual_bp.route("/apply_signature_manual", methods=["POST"])
def apply_signature_manual():

    try:
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

        # 🔥 escala
        scale_x = pdf_width / 600
        scale_y = pdf_height / 800

        x_real = x * scale_x
        y_real = pdf_height - (y * scale_y) - 100

        # 🔥 overlay
        overlay_name = f"{uuid.uuid4()}.pdf"
        overlay_path = os.path.join(UPLOAD_FOLDER, overlay_name)

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
        for path in [pdf_path, sig_path, overlay_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        print("ERROR FIRMA:", e)
        return render_template("result.html", error="Error aplicando firma")