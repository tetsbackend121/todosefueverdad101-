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

        resolution_path = os.path.join("downloads", "mp4", resolution + "p")

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

if __name__ == '__main__':
    app.run(debug=True, port=80)
