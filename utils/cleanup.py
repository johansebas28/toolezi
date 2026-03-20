import os
import time

# 📁 Ruta base del proyecto (sube un nivel desde utils/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 📂 Carpetas
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

# ⏱ Tiempo máximo en segundos (10 minutos)
MAX_AGE = 60


def clean_old_files():
    now = time.time()

    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        # 🔥 Crear carpeta si no existe (evita errores en producción)
        os.makedirs(folder, exist_ok=True)

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path):
            try:
                file_age = now - os.path.getmtime(file_path)

                if file_age > MAX_AGE:
                    os.remove(file_path)
                    print(f"🧹 Eliminado: {file_path}")

            except Exception as e:
                print(f"❌ Error eliminando {file_path}: {e}")
