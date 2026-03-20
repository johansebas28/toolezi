import os
import time

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# ⏱ tiempo máximo (ej: 10 minutos)
MAX_AGE = 600  

def clean_old_files():
    now = time.time()

    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:

        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):

            file_path = os.path.join(folder, filename)

            if os.path.isfile(file_path):

                file_age = now - os.path.getmtime(file_path)

                if file_age > MAX_AGE:
                    try:
                        os.remove(file_path)
                        print(f"🧹 Eliminado: {file_path}")
                    except Exception as e:
                        print(f"❌ Error eliminando {file_path}: {e}")