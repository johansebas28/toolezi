FROM python:3.11-slim

WORKDIR /app

# Copiar solo requirements primero (mejor cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Luego copiar el resto del proyecto
COPY . .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]