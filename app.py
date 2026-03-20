from flask import Flask, render_template, send_file
import os

from routes.merge import merge_bp
from routes.split import split_bp
from routes.convert import convert_bp
from routes.compress import compress_bp
from routes.rotate import rotate_bp
from utils.cleanup import clean_old_files
from routes.delete import delete_bp
from routes.reorder import reorder_bp
from routes.add_images import add_images_bp


app = Flask(__name__)

OUTPUT_FOLDER = "outputs"

# REGISTRAR BLUEPRINTS
app.register_blueprint(merge_bp)
app.register_blueprint(split_bp)
app.register_blueprint(convert_bp)
app.register_blueprint(compress_bp)
app.register_blueprint(rotate_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(reorder_bp)
app.register_blueprint(add_images_bp)

@app.before_request
def auto_cleanup():
    clean_old_files()

@app.route("/")
def home():
    clean_old_files()  # 🔥 limpia cada vez que alguien entra
    return render_template("index.html")

# DESCARGA + LIMPIEZA
@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join("outputs", filename)

    if not os.path.exists(path):
        return "Archivo no encontrado"

    response = send_file(path, as_attachment=True)

    # 🔥 BORRAR DESPUÉS DE ENVIAR
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
def serve_image(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename))


if __name__ == "__main__":
    app.run(debug=True)