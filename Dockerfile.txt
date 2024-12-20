# Usa una imagen base oficial de Python 3.10
FROM python:3.10-slim

# Instala las dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala pip y crea un entorno virtual
RUN python -m venv venv
RUN /app/venv/bin/pip install --upgrade pip

# Copia el archivo requirements.txt en el directorio de trabajo
COPY requirements.txt .

# Instala las dependencias del proyecto en el entorno virtual
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copia el contenido del proyecto en el directorio de trabajo
COPY . .

# Realiza las migraciones de la base de datos
RUN /app/venv/bin/python manage.py migrate

# Recoge los archivos estáticos
RUN /app/venv/bin/python manage.py collectstatic --noinput

# Expone el puerto 8080
EXPOSE 8080

# Define el comando de inicio para ejecutar el servidor Gunicorn
CMD ["/app/venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "proyecto.wsgi:application"]


