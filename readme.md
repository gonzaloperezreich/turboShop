# Proyecto de Clasificación de Modelos con Lenguaje Natural

## Descripción

Este proyecto incluye un modelo de lenguaje (LLM) entrenado con SpaCy que clasifica entradas de texto en función del lenguaje natural. El modelo permite identificar ciertas entidades dentro del texto proporcionado. La arquitectura del proyecto se divide en varias partes:

1. **Modelo LLM**: Entrenado con SpaCy para procesar y clasificar texto.
2. **Servidor Flask**: Recibe cadenas de texto como entrada y devuelve resultados basados en el análisis realizado por el modelo.
3. **Endpoint en Node.js**: Maneja la interacción con una base de datos configurada en Supabase, permitiendo realizar consultas y obtener resultados.
4. **Frontend**: Una interfaz de usuario que permite realizar consultas a la base de datos, utilizando tanto reconocimiento de lenguaje natural como búsqueda mecánica.

## Componentes del Proyecto

### 1. Modelo LLM

El modelo LLM ha sido entrenado utilizando SpaCy, una biblioteca de procesamiento de lenguaje natural en Python. Este modelo está diseñado para clasificar texto y reconocer entidades, lo que facilita la interpretación de consultas de los usuarios.

### 2. Servidor Flask

El servidor Flask actúa como intermediario entre el modelo LLM y el frontend. Este servidor expone un endpoint que permite enviar cadenas de texto para su análisis.

- **Endpoint**: `/predict`
- **Método**: `POST`
- **Entrada**: 
  - `text`: Cadena de texto a clasificar.

### 3. Endpoint en Node.js

El endpoint en Node.js se encarga de gestionar las solicitudes de búsqueda hacia la base de datos Supabase. Este endpoint permite realizar consultas basadas en las clasificaciones y entidades extraídas por el modelo LLM.

- **Endpoint**: `/check`
- **Método**: `GET`
- **Parámetros de consulta**:
  - `marca`: Marca del modelo a buscar.
  - `modelo`: Modelo del vehículo a buscar.

### 4. Frontend

La interfaz frontend permite a los usuarios interactuar con el sistema de manera sencilla. Los usuarios pueden ingresar texto natural o buscar directamente por marca y modelo. La interfaz es intuitiva y está diseñada para facilitar el acceso a la base de datos.

- **Funcionalidades**:
  - Búsqueda mediante lenguaje natural.
  - Búsqueda manual por marca y modelo.
  - Visualización de resultados en una tabla.

## Instalación y Configuración

1. **Instalar Dependencias**: Asegúrate de tener instalado Node.js y npm. Luego, ejecuta los siguientes comandos en la raíz del proyecto:

   ```bash
   npm install

2. **Correr el proyecto**
-  En la raiz del proyecto se debe correr 
   ```bash
   python app.py 
(asegurandose de tener en el ambiente local spacy y numpy) -> servidor flask localhost:5500
-  En otra terminal dirigirse a la carpeta server y ejecutar 
   ```bash
   npm run dev 
(habiendo hecho npm i previamente) 
Se debera crear un archivo .env con variables de entorno que se le serán facilitadas al evaluador por correo. -> servidor Node + Express localhost:3300
-  Finalmente para correr el frontend se debe ir a la carpeta turboClient y ejecutar 
   ```bash
   npm run dev 
localhost:3000
