const express = require('express');
const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const app = express();
const PORT = 3300;

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);
const cors = require('cors');

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('¡Bienvenido al servidor de Turboshop!');
});

// Endpoint para realizar la predicción
app.post('/predict', async (req, res) => {
    const { texts } = req.body;
    let counter = 0; // Contador de intentos de inserción repetida

    try {
        // Llama al servicio de Flask
        const response = await axios.post(`http://localhost:5500/predict`, { texts });
        const entities = response.data;

        const modelosMarcas = [];

        entities.forEach(item => {
            const validPairs = item.valid_combinations;
            const descripcion = item.description || ''; // Agrega la descripción si está disponible

            validPairs.forEach(([marca, modelo]) => {
                modelosMarcas.push({ marca, modelo, descripcion });
            });
        });

        // Inserción condicional en Supabase
        for (const modeloMarca of modelosMarcas) {
            const { marca, modelo, descripcion } = modeloMarca;
            // Verifica si ya existe una combinación de marca, modelo y descripción en Supabase
            const { data: existingEntries, error: selectError } = await supabase
                .from('ModelosMarcasAutos')
                .select('*')
                .eq('MARCA', marca)
                .eq('MODELO', modelo);

            if (selectError) {
                console.error("Error al consultar en Supabase:", selectError.message);
                continue;
            }

            // Verifica si hay un registro con la misma descripción
            const existsWithDescription = existingEntries.some(entry => entry.DESCRIPCION === descripcion);
            // Inserta solo si no existe la combinación de marca, modelo y descripción
            if (!existsWithDescription) {
                const { data, error } = await supabase
                    .from('ModelosMarcasAutos')
                    .insert([{ MARCA: marca, MODELO: modelo, DESCRIPCION: descripcion }]);

                if (error) {
                    console.error("Error al insertar en Supabase:", error.message);
                } else {
                    console.log("Marca y modelo insertados:", { marca, modelo, descripcion });
                }
            } else {
                counter++; // Incrementa el contador si ya existe la combinación
                console.log(`La combinación de marca, modelo y descripción ya existe: ${marca} ${modelo} - ${descripcion}`);
            }
        }

        res.json({ modelosMarcas, reintentos: counter });
    } catch (error) {
        console.error("Error al llamar a la API de Python:", error.message);
        res.status(500).json({ error: 'Error al procesar la solicitud.' });
    }
});

app.get('/check', async (req, res) => {
    const { marca, modelo } = req.query; // Obtener los parámetros de la consulta

    if (!marca || !modelo) {
        return res.status(400).json({ error: 'Se requieren marca y modelo como parámetros de consulta.' });
    }

    try {
        // Consultar en Supabase
        const { data: existingEntries, error: selectError } = await supabase
            .from('ModelosMarcasAutos')
            .select('*')
            .eq('MARCA', marca)
            .eq('MODELO', modelo);

        if (selectError) {
            console.error("Error al consultar en Supabase:", selectError.message);
            return res.status(500).json({ error: 'Error al consultar en la base de datos.' });
        }

        // Verificar si hay coincidencias
        if (existingEntries.length > 0) {
            res.json({ exists: true, entries: existingEntries });
        } else {
            res.json({ exists: false });
        }
    } catch (error) {
        console.error("Error al procesar la solicitud:", error.message);
        res.status(500).json({ error: 'Error al procesar la solicitud.' });
    }
});
const FuzzySet = require('fuzzyset.js');

app.get('/checkByNameAndBand', async (req, res) => {
    const { marca, modelo } = req.query;

    if (!marca || !modelo) {
        return res.status(400).json({ error: 'Se requieren marca y modelo como parámetros de consulta.' });
    }

    try {
        const { data: existingEntries, error: selectError } = await supabase
            .from('ModelosMarcasAutos')
            .select('*');

        if (selectError) {
            console.error("Error al consultar en Supabase:", selectError.message);
            return res.status(500).json({ error: 'Error al consultar en la base de datos.' });
        }

        // Coincidencias exactas
        const exactMatches = existingEntries.filter(entry => 
            entry.MARCA.toLowerCase() === marca.toLowerCase() &&
            entry.MODELO.toLowerCase() === modelo.toLowerCase()
        );

        if (exactMatches.length > 0) {
            return res.json({ exists: true, entries: exactMatches });
        }

        // Crear un conjunto difuso para marcas y modelos existentes
        const marcasSet = FuzzySet(existingEntries.map(entry => entry.MARCA.toLowerCase()));
        const modelosSet = FuzzySet(existingEntries.map(entry => entry.MODELO.toLowerCase()));

        // Buscar coincidencias similares
        const marcaSimilares = marcasSet.get(marca.toLowerCase());
        const modeloSimilares = modelosSet.get(modelo.toLowerCase());

        // Filtrar entradas similares
        const similarEntries = existingEntries.filter(entry => 
            (marcaSimilares && marcaSimilares.some(([match]) => match === entry.MARCA.toLowerCase())) ||
            (modeloSimilares && modeloSimilares.some(([match]) => match === entry.MODELO.toLowerCase()))
        );

        if (similarEntries.length > 0) {
            return res.json({ exists: true, entries: similarEntries });
        } else {
            return res.json({ exists: false });
        }

    } catch (error) {
        console.error("Error al procesar la solicitud:", error.message);
        res.status(500).json({ error: 'Error al procesar la solicitud.' });
    }
});
app.listen(PORT, () => {
  console.log('Servidor corriendo, escuchando en el puerto', PORT);
});
