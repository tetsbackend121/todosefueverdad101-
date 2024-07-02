const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require("cors")

const app = express();
const port = 8080;

const db = 'mongodb+srv://reypele18:mierda@dealgo.psquqeb.mongodb.net/IPCONFIG?retryWrites=true&w=majority&appName=dealgo';
const corsOptions = {
    origin: 'http://127.0.0.1:8080', // Permitir solo este origen
    methods: ['GET', 'POST'], // Permitir solo estos métodos HTTP
    allowedHeaders: ['Content-Type'], // Permitir solo estos encabezados
    optionsSuccessStatus: 200 // Algunos navegadores no envían 'OPTIONS' automáticamente, por lo que la respuesta de éxito se debe configurar explícitamente
};

// Habilitar CORS con las opciones definidas
//app.use(cors(corsOptions));

mongoose.connect(db, {}).then(() => {
    console.log("Conexión exitosa a la base de datos");
}).catch((error) => {
    console.error("Error al conectar a la base de datos:", error);
});

const IPCONFIGSchema = mongoose.Schema({
    ip: { type: String, required: true },
    name: { type: String, required: true },
});

const LINKSchema = mongoose.Schema({
    link: { type: String, required: true },
    resolution: { type: String},
    format: { type: String, required: true }
});

const IPCONFIGModel = mongoose.model("IPCONFIG", IPCONFIGSchema, "IPCONFIG");

const LINKSModel = mongoose.model("LINKS", LINKSchema, "LINKS");

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(bodyParser.json({ limit: '100mb' })); // Aumenta el límite de carga útil a 10 megabytes

app.get('/', async (req, res) => {
    res.send("Hola iditoa")
})
app.post('/uploadLink', async (req, res) => {
    // Obtener el ID desde los parámetros de la URL
    const {link, resolution, format} = req.body
    const nameServer = "NGROK"

    try {
        // Asegurarse de que el id sea un ObjectId válido
        //if (!mongoose.Types.ObjectId.isValid(id)) {
          //  return res.status(400).json({ mensaje: 'ID no válido' });
        //}

        const URL_NGROK = await IPCONFIGModel.findOne({ name: "NGROK"});
        const ipNGROK = URL_NGROK.ip

        const newData = {
            link: link,
            resolution: resolution,
            format: format
        };

        const exampleInstance = new LINKSModel(newData);
        exampleInstance.save()

        // Configuración de la solicitud
        const requestOptions = {
            method: 'POST',         // Método HTTP POST
            headers: {
                'Content-Type': 'application/json'  // Tipo de contenido JSON
            },
            body: JSON.stringify(newData)  // Convertir el objeto a formato JSON
        };

        // Realizar la solicitud POST usando fetch
        fetch(ipNGROK+"/uploadLink", requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Hubo un problema al realizar la solicitud: ' + response.statusText);
                }
                return response.json();  // Convertir la respuesta a JSON
            })
            .then(data => {
                console.log('Respuesta del servidor:', data);
                code = data.blob_url
                console.log(code)
                
                return res.status(200).json()
                // Manejar la respuesta del servidor aquí
            })
            .catch(error => {
                console.error('Error al realizar la solicitud:', error);
    });



        // Intentar eliminar el documento
        const deleteResult = "ddd"//await IPCONFIGModel.deleteOne({ name: nameServer});

        if (deleteResult.deletedCount === 0) {
            return res.status(404).json({ mensaje: 'No se encontró ningún documento con el ID especificado' });
        }

        // Documento eliminado correctamente
        res.status(200).json({ mensaje: 'Documento eliminado correctamente' });

    } catch (error) {
        console.log('Error al eliminar el documento:', error);
        res.status(500).json({ mensaje: 'Error en el servidor' });
    }
});


app.listen(port, () => {
    console.log(`Servidor Express escuchando en el puerto ${port}`);
});
