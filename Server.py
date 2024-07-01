from flask import Flask, request, jsonify, make_response, send_file
from pymongo import MongoClient
from cerberus import Validator
import modulos.download_link as download_link
import io
import os
import uuid

app = Flask(__name__, static_url_path='/public', static_folder='public')

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

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

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

        nombrefile = download_link.ConvertMP4(url, resolution + "p")

        file_path = f"downloads/mp4/{resolution}p/{nombrefile}"

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
    app.run(debug=True, port=80)
