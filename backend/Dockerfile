# Dockerfile optimizado para Cloud Run
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Exponer puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1

