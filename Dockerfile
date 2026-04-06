FROM python:3.11-slim

WORKDIR /app

# 🔥 Instalar TODAS las dependencias necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libx11-6 \
    libxcb1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar Python libs
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]