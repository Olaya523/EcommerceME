# Usa una imagen de Python 3.9 como base
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install -r requirements.txt

# Copia todo el contenido del directorio actual al contenedor en /app
COPY . .

# Indica qué comandos deben ejecutarse cuando se inicie el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

