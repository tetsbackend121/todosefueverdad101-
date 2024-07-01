from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
from cerberus import Validator
import modulos.download_link as download_link
import os
import uuid

app = Flask(__name__)

# Conectar a MongoDB
client = MongoClient('mongodb+srv://reypele18:mierda@dealgo.psquqeb.mongodb.net/downloads?retryWrites=true&w=majority&appName=dealgo')
db = client['downloads']
collection = db['files']

# Definir el esquema de validación
link_schema = {
    'name': {'type': 'string', 'required': True},
    'format': {'type': 'string', 'required': True},
    'file_path': {'type': 'string', 'required': True},
    'blob_id': {'type': 'string', 'required': True},
    'resolution': {'type': 'string'}
}

# Crear un validador
v = Validator(link_schema)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://frontendconvert.onrender.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def index():
    return "Hola mundo python"

@app.route('/uploadLink', methods=['POST'])
def convertir():
    global nombrefile
    datos = request.json

    format = datos.get("format")

    if not format:
        return jsonify({"message": "Formato no especificado"}), 400

    if format == "MP4":
        url = datos.get("link")
        resolution = datos.get("resolution")

        if not url or not resolution:
            return jsonify({"message": "Link o resolución no especificados"}), 400

        resolution_path = f"downloads/mp4/{resolution}p"
        
        # Crear el directorio si no existe
        os.makedirs(resolution_path, exist_ok=True)

        nombrefile = download_link.ConvertMP4(url, resolution + "p")

        file_path = os.path.join(resolution_path, nombrefile)

        if not os.path.exists(file_path):
            return jsonify({"message": "Archivo no encontrado"}), 404

        blob_id = str(uuid.uuid4())

        ParaSchema = {
            "blob_id": blob_id,
            'name': nombrefile,
            'format': format,
            'file_path': file_path,
            'resolution': resolution
        }

        if not v.validate(ParaSchema):
            return jsonify({'error': v.errors}), 400

        collection.insert_one(ParaSchema)

        # Generar el enlace al blob
        blob_url = f'/blobs/{blob_id}'

        # Devolver una respuesta JSON con el enlace al blob
        return jsonify({"blob_url": blob_url})

    elif format == "MP3":
        url = datos.get("link")

        if not url:
            return jsonify({"message": "Link no especificado"}), 400

        nombrefile = download_link.ConvertMP3(url)

        file_path = f"downloads/mp3/{nombrefile}"

        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if not os.path.exists(file_path):
            return jsonify({"message": "Archivo no encontrado"}), 404

        blob_id = str(uuid.uuid4())

        ParaSchema = {
            "blob_id": blob_id,
            'name': nombrefile,
            'format': format,
            'file_path': file_path
        }

        if not v.validate(ParaSchema):
            return jsonify({'error': v.errors}), 400

        collection.insert_one(ParaSchema)

        # Generar el enlace al blob
        blob_url = f'/blobs/{blob_id}'

        return jsonify({"blob_url": blob_url})

    else:
        return jsonify({"message": "Formato no soportado"}), 400

@app.route('/blobs/<blob_id>', methods=['GET'])
def download_blob(blob_id):
    # Buscar el documento en MongoDB por blob_id
    resultado = collection.find_one({"blob_id": blob_id})

    if resultado:
        file_path = resultado['file_path']
        
        if not os.path.exists(file_path):
            return 'Archivo no encontrado', 404

        # Crear una respuesta Flask para enviar el archivo como adjunto
        return send_file(file_path, as_attachment=True, download_name=resultado['name'])

    else:
        return 'Archivo no encontrado en MongoDB', 404

if __name__ == '__main__':
    import os
    from werkzeug.middleware.shared_data import SharedDataMiddleware

    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True, port=80)
    else:
        # Ejecutar la aplicación con Gunicorn en producción
        from gunicorn.app.base import BaseApplication

        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        options = {
            'bind': '0.0.0.0:80',
            'workers': 4,  # Número de workers que quieres configurar
            'accesslog': '-',  # Log de acceso a la consola
            'errorlog': '-',  # Log de errores a la consola
        }

        StandaloneApplication(app, options).run()
