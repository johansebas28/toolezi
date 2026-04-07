from flask import Flask, render_template, send_file, send_from_directory
import os

from routes.merge import merge_bp
from routes.split import split_bp
from routes.convert import convert_bp
from routes.excel import excel_bp
from routes.pdf_to_excel import pdf_excel_bp
from routes.powerpoint import ppt_bp
from routes.compress import compress_bp
from routes.rotate import rotate_bp
from utils.cleanup import clean_old_files
from routes.delete import delete_bp
from routes.reorder import reorder_bp
from routes.add_images import add_images_bp
from routes.unlock import unlock_bp
from routes.protect import protect_bp
from routes.watermark import watermark_bp
from routes.sign import sign_bp
from routes.ocr import ocr_bp
from routes.number_pages import number_bp
from routes.sign_manual import sign_manual_bp

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

# REGISTRAR BLUEPRINTS
app.register_blueprint(merge_bp)
app.register_blueprint(split_bp)
app.register_blueprint(convert_bp)
app.register_blueprint(excel_bp)
app.register_blueprint(pdf_excel_bp)
app.register_blueprint(ppt_bp)
app.register_blueprint(compress_bp)
app.register_blueprint(rotate_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(reorder_bp)
app.register_blueprint(add_images_bp)
app.register_blueprint(unlock_bp)
app.register_blueprint(protect_bp)
app.register_blueprint(watermark_bp)
app.register_blueprint(sign_bp)
app.register_blueprint(ocr_bp)
app.register_blueprint(number_bp)
app.register_blueprint(sign_manual_bp)

@app.before_request
def auto_cleanup():
    clean_old_files()

from flask import send_from_directory

@app.route("/")
def home():
    clean_old_files()  # 🔥 limpia cada vez que alguien entra
    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(path):
        return f"Archivo no encontrado: {filename}"

    response = send_file(path, as_attachment=True)


    @response.call_on_close
    def cleanup():
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print("Error al borrar:", e)

    return response


# SERVIR IMÁGENES
@app.route("/image/<filename>")
def get_image(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    outputs_dir = os.path.join(base_dir, "outputs")

    filename = os.path.basename(filename)

    full_path = os.path.join(outputs_dir, filename)

    if os.path.exists(full_path):
        return send_from_directory(OUTPUT_FOLDER, filename, conditional=True)

    print("❌ NO ENCONTRADA:", full_path)
    return "Imagen no encontrada", 404


if __name__ == "__main__":
    app.run(debug=True)
