# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requisitos al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tu proyecto al contenedor
COPY . .

# Establece la variable de entorno de Django
ENV DJANGO_SETTINGS_MODULE=proyecto.settings

# Expone el puerto en el que se ejecuta la aplicación
EXPOSE 8000

# Ejecuta las migraciones y el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]



