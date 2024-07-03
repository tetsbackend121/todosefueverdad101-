const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require("cors")

const app = express();
const port = 80;

const db = 'mongodb+srv://reypele18:mierda@dealgo.psquqeb.mongodb.net/IPCONFIG?retryWrites=true&w=majority&appName=dealgo';
const corsOptions = {
    origin: 'https://frontendconvert.onrender.com', // Permitir solo este origen
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

app.use(express.json());
app.use(bodyParser.json({ limit: '100mb' })); // Aumenta el límite de carga útil a 10 megabytes

app.post('/', async (req, res) => {

    console.log("Alguien post hizo.")
    
    // Obtener el ID desde los parámetros de la URL
    const nameServer = "NGROK"
    const URL_NGROK = await IPCONFIGModel.findOne({ name: "NGROK"});
    const ipNGROK = URL_NGROK.ip

    res.send(ipNGROK)


});


app.listen(port, () => {
    console.log(`Servidor Express escuchando en el puerto ${port}`);
});
