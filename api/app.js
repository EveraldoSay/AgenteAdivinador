const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Configuración de la conexión a la base de datos
const dbConfig = {
  host: process.env.DB_HOST || '127.0.0.1',
  port: process.env.DB_PORT || '3308',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'agenteadivinador'
};

// Pool de conexiones para mejor rendimiento
let pool;

async function initializeConnectionPool() {
  try {
    pool = mysql.createPool(dbConfig);
    console.log('Conexión a la base de datos establecida');
  } catch (error) {
    console.error('Error al conectar a la base de datos:', error);
    process.exit(1);
  }
}

// Rutas de la API

// Obtener todos los países
app.get('/api/paises', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM paises ORDER BY nombre');
    res.json(rows);
  } catch (error) {
    console.error('Error al obtener países:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener mundiales por país
app.get('/api/paises/:id/mundiales', async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT * FROM mundiales WHERE pais_id = ? ORDER BY anio',
      [req.params.id]
    );
    res.json(rows);
  } catch (error) {
    console.error('Error al obtener mundiales:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener mundiales con información del país
app.get('/api/mundiales', async (req, res) => {
  try {
    const [rows] = await pool.query(
      `SELECT m.id, m.anio, p.id as pais_id, p.nombre as pais
       FROM mundiales m
       JOIN paises p ON m.pais_id = p.id
       ORDER BY m.anio DESC`
    );
    res.json(rows);
  } catch (error) {
    console.error('Error al obtener mundiales:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener detalles de un mundial específico
app.get('/api/mundiales/:id', async (req, res) => {
  try {
    const [mundialRows] = await pool.query(
      `SELECT m.id, m.anio, p.id as pais_id, p.nombre as pais
       FROM mundiales m
       JOIN paises p ON m.pais_id = p.id
       WHERE m.id = ?`, [req.params.id]
    );

    if (mundialRows.length === 0) {
      return res.status(404).json({ error: 'Mundial no encontrado' });
    }

    const mundial = mundialRows[0];

    const [jugadoresRows] = await pool.query(
      `SELECT j.id, j.nombre, p.nombre as posicion, p.abreviatura as posicion_abr, j.titular
       FROM jugadores j
       JOIN posiciones p ON j.posicion_id = p.id
       WHERE j.mundial_id = ?
       ORDER BY 
         CASE 
           WHEN p.nombre = 'Portero' THEN 1
           WHEN p.nombre = 'Defensa' THEN 2
           WHEN p.nombre = 'Mediocampista' THEN 3
           WHEN p.nombre = 'Delantero' THEN 4
         END,
         j.titular DESC,
         j.nombre`, [req.params.id]
    );

    mundial.jugadores = {
      titulares: jugadoresRows.filter(j => j.titular),
      suplentes: jugadoresRows.filter(j => !j.titular)
    };

    res.json(mundial);
  } catch (error) {
    console.error('Error al obtener detalles del mundial:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Búsqueda de jugadores
app.get('/api/jugadores/buscar', async (req, res) => {
  try {
    const busqueda = req.query.q || '';
    if (busqueda.length < 3) {
      return res.status(400).json({ error: 'La búsqueda debe tener al menos 3 caracteres' });
    }

    const [rows] = await pool.query(
      `SELECT j.id, j.nombre, pos.nombre as posicion, p.nombre as pais, m.anio,
              j.titular
       FROM jugadores j
       JOIN mundiales m ON j.mundial_id = m.id
       JOIN paises p ON m.pais_id = p.id
       JOIN posiciones pos ON j.posicion_id = pos.id
       WHERE j.nombre LIKE ?
       ORDER BY m.anio DESC, j.nombre`, [`%${busqueda}%`]
    );

    res.json(rows);
  } catch (error) {
    console.error('Error al buscar jugadores:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Inicializar la aplicación
async function startServer() {
  await initializeConnectionPool();
  
  app.listen(port, () => {
    console.log(`Servidor escuchando en el puerto ${port}`);
  });
}

startServer();

module.exports = app;