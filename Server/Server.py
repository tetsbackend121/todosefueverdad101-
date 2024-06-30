from flask import Flask, request, jsonify, make_response, send_file
import modulos.download_link as download_link
import io
import uuid

app = Flask(__name__, static_url_path='/public', static_folder='public')

blobs = {}

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

        try:
            with open(file_path, "rb") as file:
                data = file.read()
        except FileNotFoundError:
            return jsonify({"message": "Archivo no encontrado"}), 404

        # Crear un objeto BytesIO para simular un Blob
        blob = io.BytesIO()
        blob.write(data)
        blob.seek(0)

        # Generar un ID único para este Blob
        blob_id = str(uuid.uuid4())
        
        # Guardar el Blob en el diccionario usando el ID como clave
        blobs[blob_id] = blob

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

        try:
            with open(file_path, "rb") as file:
                data = file.read()
        except FileNotFoundError:
            return jsonify({"message": "Archivo no encontrado"}), 404

        blob = io.BytesIO(data)
        blob_id = str(uuid.uuid4())
        blobs[blob_id] = blob

        blob_url = f'/blobs/{blob_id}'

        return jsonify({"blob_url": blob_url})


    else:
        return jsonify({"message": "Formato no soportado"}), 400

@app.route('/blobs/<blob_id>', methods=['GET'])
def download_blob(blob_id):
    # Obtener el Blob del diccionario usando el ID
    blob = blobs.get(blob_id)
    if blob:
        try:
            # Crear una respuesta Flask para enviar el Blob como archivo adjunto
            response = make_response(send_file(blob, as_attachment=True, download_name=f'{nombrefile}'))
            response.headers['Content-Disposition'] = f'attachment; filename={nombrefile}'
            return response
        
        except ValueError:
            # Si el archivo está cerrado, devolver un error
            return 'Archivo no disponible o ya descargado', 410
    else:
        return 'Archivo no encontrado', 404

if __name__ == '__main__':
    app.run(debug=True, port=80)
