from flask import Blueprint, request, render_template
import pdfplumber
import pandas as pd
import os, uuid

pdf_excel_bp = Blueprint("pdf_excel", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")


@pdf_excel_bp.route("/pdf_to_excel", methods=["POST"])
def pdf_to_excel():

    file = request.files.get("pdf")

    if not file:
        return render_template("result.html", error="No file provided")

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
    file.save(input_path)

    output_filename = f"{uuid.uuid4()}.xlsx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        all_tables = []

        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables.append(df)

        if not all_tables:
            os.remove(input_path)
            return render_template("result.html", error="No tables found in PDF")

        # 🔥 guardar en Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f"Table_{i+1}", index=False)

        os.remove(input_path)

        return render_template("result.html", filename=output_filename)

    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return render_template("result.html", error="Error converting PDF to Excel")