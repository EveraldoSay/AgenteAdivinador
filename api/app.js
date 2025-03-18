// mundiales-api/app.js
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
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  port: process.env.DB_PORT || '3308',
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
    const [rows] = await pool.query(`
      SELECT m.id, m.anio, p.id as pais_id, p.nombre as pais
      FROM mundiales m
      JOIN paises p ON m.pais_id = p.id
      ORDER BY m.anio DESC
    `);
    res.json(rows);
  } catch (error) {
    console.error('Error al obtener mundiales:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener detalles de un mundial específico
app.get('/api/mundiales/:id', async (req, res) => {
  try {
    // Obtenemos la información del mundial
    const [mundialRows] = await pool.query(`
      SELECT m.id, m.anio, p.id as pais_id, p.nombre as pais
      FROM mundiales m
      JOIN paises p ON m.pais_id = p.id
      WHERE m.id = ?
    `, [req.params.id]);

    if (mundialRows.length === 0) {
      return res.status(404).json({ error: 'Mundial no encontrado' });
    }

    const mundial = mundialRows[0];

    // Obtenemos los jugadores de ese mundial
    const [jugadoresRows] = await pool.query(`
      SELECT j.id, j.nombre, p.nombre as posicion, p.id as posicion_id, p.abreviatura as posicion_abr, j.titular
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
        j.nombre
    `, [req.params.id]);

    // Armamos la respuesta completa
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

    const [rows] = await pool.query(`
      SELECT j.id, j.nombre, pos.nombre as posicion, p.nombre as pais, m.anio,
             j.titular
      FROM jugadores j
      JOIN mundiales m ON j.mundial_id = m.id
      JOIN paises p ON m.pais_id = p.id
      JOIN posiciones pos ON j.posicion_id = pos.id
      WHERE j.nombre LIKE ?
      ORDER BY m.anio DESC, j.nombre
    `, [`%${busqueda}%`]);

    res.json(rows);
  } catch (error) {
    console.error('Error al buscar jugadores:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener todas las posiciones
app.get('/api/posiciones', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM posiciones ORDER BY id');
    res.json(rows);
  } catch (error) {
    console.error('Error al obtener posiciones:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Crear un nuevo país
app.post('/api/paises', async (req, res) => {
  try {
    const { nombre } = req.body;
    
    if (!nombre) {
      return res.status(400).json({ error: 'El nombre del país es obligatorio' });
    }
    
    // Verificar si ya existe
    const [existingRows] = await pool.query('SELECT id FROM paises WHERE nombre = ?', [nombre]);
    if (existingRows.length > 0) {
      return res.json(existingRows[0]); // Devolver el existente
    }
    
    // Insertar nuevo país
    const [result] = await pool.query('INSERT INTO paises (nombre) VALUES (?)', [nombre]);
    
    res.json({
      id: result.insertId,
      nombre
    });
  } catch (error) {
    console.error('Error al crear país:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Crear un nuevo mundial
app.post('/api/mundiales', async (req, res) => {
  try {
    const { anio, pais_id } = req.body;
    
    if (!anio || !pais_id) {
      return res.status(400).json({ error: 'El año y el país son obligatorios' });
    }
    
    // Verificar si ya existe
    const [existingRows] = await pool.query(
      'SELECT id FROM mundiales WHERE anio = ? AND pais_id = ?', 
      [anio, pais_id]
    );
    
    if (existingRows.length > 0) {
      // Si ya existe, obtener detalles
      const [mundialRows] = await pool.query(`
        SELECT m.id, m.anio, p.id as pais_id, p.nombre as pais
        FROM mundiales m
        JOIN paises p ON m.pais_id = p.id
        WHERE m.id = ?
      `, [existingRows[0].id]);
      
      return res.json(mundialRows[0]); // Devolver el existente
    }
    
    // Insertar nuevo mundial
    const [result] = await pool.query(
      'INSERT INTO mundiales (anio, pais_id) VALUES (?, ?)',
      [anio, pais_id]
    );
    
    // Obtener detalles del país
    const [paisRows] = await pool.query('SELECT nombre FROM paises WHERE id = ?', [pais_id]);
    
    res.json({
      id: result.insertId,
      anio,
      pais_id,
      pais: paisRows[0]?.nombre || 'Desconocido'
    });
  } catch (error) {
    console.error('Error al crear mundial:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Crear un nuevo jugador
app.post('/api/jugadores', async (req, res) => {
  try {
    const { nombre, mundial_id, posicion_id, titular } = req.body;
    
    if (!nombre || !mundial_id || !posicion_id) {
      return res.status(400).json({ error: 'El nombre, mundial y posición son obligatorios' });
    }
    
    // Verificar si ya existe
    const [existingRows] = await pool.query(
      'SELECT id FROM jugadores WHERE nombre = ? AND mundial_id = ?', 
      [nombre, mundial_id]
    );
    
    if (existingRows.length > 0) {
      // Si ya existe, obtener detalles
      const [jugadorRows] = await pool.query(`
        SELECT j.id, j.nombre, pos.nombre as posicion, pos.id as posicion_id, 
               p.nombre as pais, m.anio, j.titular, m.id as mundial_id
        FROM jugadores j
        JOIN mundiales m ON j.mundial_id = m.id
        JOIN paises p ON m.pais_id = p.id
        JOIN posiciones pos ON j.posicion_id = pos.id
        WHERE j.id = ?
      `, [existingRows[0].id]);
      
      return res.json(jugadorRows[0]); // Devolver el existente
    }
    
    // Insertar nuevo jugador
    const [result] = await pool.query(
      'INSERT INTO jugadores (nombre, mundial_id, posicion_id, titular) VALUES (?, ?, ?, ?)',
      [nombre, mundial_id, posicion_id, titular ? 1 : 0]
    );
    
    // Obtener detalles del jugador recién creado
    const [jugadorRows] = await pool.query(`
      SELECT j.id, j.nombre, pos.nombre as posicion, pos.id as posicion_id, 
             p.nombre as pais, m.anio, j.titular, m.id as mundial_id
      FROM jugadores j
      JOIN mundiales m ON j.mundial_id = m.id
      JOIN paises p ON m.pais_id = p.id
      JOIN posiciones pos ON j.posicion_id = pos.id
      WHERE j.id = ?
    `, [result.insertId]);
    
    res.json(jugadorRows[0] || {
      id: result.insertId,
      nombre,
      mundial_id,
      posicion_id,
      titular: !!titular
    });
  } catch (error) {
    console.error('Error al crear jugador:', error);
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
