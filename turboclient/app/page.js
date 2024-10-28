"use client"; // Añadir esta línea
import { useState } from 'react';

export default function Home() {
  const [inputText, setInputText] = useState('');
  const [marca, setMarca] = useState('');
  const [modelo, setModelo] = useState('');
  const [classification, setClassification] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false); // Estado para la carga
  const [searched, setSearched] = useState(false); // Estado para indicar si se realizó una búsqueda

  const handlePredictSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Activar el loading
    setSearched(true); // Marcar que se ha realizado una búsqueda
    setResults([]); // Limpiar resultados antes de la nueva búsqueda

    try {
      // Realizar la búsqueda basada en el texto ingresado
      const response = await fetch('http://localhost:5500/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ texts: [inputText] }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const validCombinations = data[0].valid_combinations;

      const fetchPromises = validCombinations.map(async ([marca, modelo]) => {
        const checkResponse = await fetch(`http://localhost:3300/check?marca=${marca.toLowerCase()}&modelo=${modelo.toLowerCase()}`);
        if (!checkResponse.ok) {
          throw new Error('Error al consultar la base de datos');
        }
        return await checkResponse.json(); // Devuelve la respuesta como JSON
      });

      const allResults = await Promise.all(fetchPromises);
      setResults(allResults);
      setClassification(data);
    } catch (error) {
      console.error('Error al enviar el input:', error);
      setClassification('Error al obtener la clasificación');
    } finally {
      setLoading(false); // Desactivar el loading
      setInputText(''); // Limpiar el input después de la búsqueda
    }
  };

  const handleManualSearch = async (e) => {
    e.preventDefault();
    setLoading(true); // Activar el loading
    setSearched(true); // Marcar que se ha realizado una búsqueda

    if (marca && modelo) {
      try {
        const checkResponse = await fetch(`http://localhost:3300/check?marca=${marca.toLowerCase()}&modelo=${modelo.toLowerCase()}`);
        if (!checkResponse.ok) {
          throw new Error('Error al consultar la base de datos');
        }
        const result = await checkResponse.json();
        setResults((prevResults) => [...prevResults, result]); // Combina los resultados
      } catch (error) {
        console.error('Error al consultar por marca y modelo:', error);
      } finally {
        setLoading(false); // Desactivar el loading
        setMarca(''); // Limpiar el input de marca
        setModelo(''); // Limpiar el input de modelo
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <form onSubmit={handlePredictSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-96">
        <h2 className="text-2xl font-bold mb-4 text-center">Clasificador de Modelos con modelo de reconocimiento inteligente</h2>
        <p className="text-center mb-4">Aqui se puede ingresar lenguaje natural y el modelo en el servidor buscará por la mejor coincidencia (el texto puede estar mal escrito, por ejemplo hiunda accent):</p>
        
        <div className="mb-4">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="ej: Repuesto para hyundai accent 2015"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <button 
          type="submit"
          className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={loading} // Desactiva el botón mientras carga
        >
          {loading ? 'Cargando...' : 'Buscar por Texto'}
        </button>
      </form>

      <form onSubmit={handleManualSearch} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-96">
        <h3 className="text-lg font-bold mb-2">Opción de búsqueda por Marca y Modelo:</h3>
        <div className="mb-4">
          <input
            type="text"
            value={marca}
            onChange={(e) => setMarca(e.target.value)}
            placeholder="Marca"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>
        <div className="mb-4">
          <input
            type="text"
            value={modelo}
            onChange={(e) => setModelo(e.target.value)}
            placeholder="Modelo"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>

        <button 
          type="submit"
          className={`bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={loading} // Desactiva el botón mientras carga
        >
          {loading ? 'Cargando...' : 'Buscar por Marca y Modelo'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-96 overflow-x-auto">
          <h3 className="text-xl font-bold mb-2">Resultados de las Consultas:</h3>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Marca</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Modelo</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Descripción</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
  {results && results.length > 0 ? (
    results.flatMap((result, index) => 
      result.entries && result.entries.length > 0 ? (
        result.entries.map((entry, entryIndex) => (
          <tr key={`${index}-${entryIndex}`}>
            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{entry.MARCA}</td>
            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{entry.MODELO}</td>
            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{entry.DESCRIPCION}</td>
          </tr>
        ))
      ) : (
        <tr key={index}>
          <td colSpan="2" className="px-4 py-2 text-center text-sm text-gray-500">
            No hay entradas para mostrar.
          </td>
        </tr>
      )
    )
  ) : (
    <tr>
      <td colSpan="2" className="px-4 py-2 text-center text-sm text-gray-500">
        No hay resultados disponibles.
      </td>
    </tr>
  )}
</tbody>

          </table>
        </div>
      )}
      {searched && results.length === 0 && (
        <h3 className="text-xl font-bold mb-2">No se encontraron relaciones</h3>
      )}
    </div>
  );
}
