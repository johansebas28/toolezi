import os
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

MAX_AGE = 60  # 1 minuto para pruebas


def clean_old_files():
    now = time.time()

    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:

        # crear carpeta si no existe
        os.makedirs(folder, exist_ok=True)

        print(f"📂 Revisando: {folder}")

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            if os.path.isfile(file_path):
                try:
                    file_age = now - os.path.getmtime(file_path)

                    print(f"Archivo: {filename} | Edad: {file_age:.2f}s")

                    if file_age > MAX_AGE:
                        os.remove(file_path)
                        print(f"🧹 Eliminado: {file_path}")

                except Exception as e:
                    print(f"❌ Error eliminando {file_path}: {e}")
