from flask import Flask, request, jsonify, make_response, send_file
import modulos.download_link as download_link
import io
import uuid

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://frontendconvert.onrender.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

blobs = {}

# Ruta para responder con "Hola, mundo"
@app.route('/')
def hello_world():
    return 'Hola, mundo!'

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
            

        nombrefile = download_link.ConvertMP4("https://www.youtube.com/watch?v=5abamRO41fE", resolution + "p")

        file_path = f"downloads/mp4/{resolution}p/{nombrefile}"

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
    blob = blobs.get(blob_id)
    if blob:
        try:
            response = make_response(send_file(blob, as_attachment=True, attachment_filename=f'{nombrefile}'))
            response.headers['Content-Disposition'] = f'attachment; filename={nombrefile}'
            return response
        except ValueError:
            return 'Archivo no disponible o ya descargado', 410
    else:
        return 'Archivo no encontrado', 404

if __name__ == '__main__':
    import os
    from werkzeug.middleware.shared_data import SharedDataMiddleware

    # Añadir middleware para servir archivos estáticos
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/public': os.path.join(os.path.dirname(__file__), 'public')
    })

    # Ejecutar la aplicación con Gunicorn en lugar del servidor de desarrollo
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
