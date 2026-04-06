# Imagen base
FROM python:3.11-slim

# Evita prompts
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# Crear carpeta de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto
ENV PORT=10000

# Ejecutar app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]