from flask import Flask, render_template, request, jsonify, session
from mundiales_akinator import MundialesAkinator
from mundiales_agent import MundialesAgent
from mundiales_agent_bert import MundialesAgentBERT
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-para-sesiones")

# Inicializar agentes
akinator = MundialesAkinator(api_url=os.getenv("API_BASE_URL", "http://localhost:3000/api"))
agente = MundialesAgent()
agente_bert = MundialesAgentBERT(api_url=os.getenv("API_BASE_URL", "http://localhost:3000/api"))

# Rutas para la aplicación
@app.route('/')
def index():
    return render_template('index.html')

# Rutas para el Akinator
@app.route('/akinator')
def akinator_index():
    return render_template('akinator.html')

@app.route('/api/iniciar', methods=['POST'])
def iniciar_juego():
    datos = request.json
    modo = datos.get('modo', 'equipo')
    
    # Iniciar el juego de Akinator
    mensaje = akinator.iniciar_juego(modo)
    
    # Guardar estado en sesión
    session['akinator_estado'] = akinator.estado
    
    # Generar primera pregunta
    pregunta = akinator.hacer_pregunta()
    
    return jsonify({
        'mensaje': mensaje,
        'pregunta': pregunta
    })

@app.route('/api/responder', methods=['POST'])
def procesar_respuesta():
    datos = request.json
    respuesta = datos.get('respuesta', '')
    
    # Recuperar estado de la sesión
    if 'akinator_estado' in session:
        akinator.estado = session['akinator_estado']
    
    # Procesar la respuesta de Akinator
    resultado = akinator.procesar_respuesta(respuesta)
    
    # Guardar estado actualizado en la sesión
    session['akinator_estado'] = akinator.estado
    
    return jsonify({
        'resultado': resultado,
        'es_final': "¿Quieres jugar de nuevo?" in resultado or "¿Quieres intentar de nuevo?" in resultado
    })

# Rutas para el Agente de Consultas (BERT)
@app.route('/entrenar')
def entrenar_index():
    return render_template('entrenar.html')

@app.route('/api/consulta', methods=['POST'])
def procesar_consulta():
    datos = request.json
    consulta = datos.get('consulta', '')
    
    if not consulta:
        return jsonify({'error': 'No se proporcionó ninguna consulta'}), 400
    
    # Procesar la consulta con el agente BERT
    respuesta = agente_bert.procesar_consulta(consulta)
    
    # Obtener el análisis BERT para información adicional (opcional)
    analisis = agente_bert.nlp.analyze_query(consulta)
    
    return jsonify({
        'respuesta': respuesta,
        'analisis': {
            'intencion': analisis['intent'],
            'confianza': float(analisis['intent_confidence']),
            'entidades': analisis['entities']
        }
    })

@app.route('/api/paises')
def obtener_paises():
    paises = agente_bert.get_paises()
    return jsonify(paises)

@app.route('/api/mundiales')
def obtener_mundiales():
    mundiales = agente_bert.get_mundiales()
    return jsonify(mundiales)

@app.route('/api/mundiales/<int:mundial_id>')
def obtener_mundial(mundial_id):
    mundial = agente_bert.get_mundial_detalle(mundial_id)
    if mundial:
        return jsonify(mundial)
    return jsonify({'error': 'Mundial no encontrado'}), 404

@app.route('/api/jugadores/buscar')
def buscar_jugadores():
    nombre = request.args.get('q', '')
    if len(nombre) < 3:
        return jsonify({'error': 'La búsqueda debe tener al menos 3 caracteres'}), 400
    
    jugadores = agente_bert.buscar_jugador(nombre)
    return jsonify(jugadores)

@app.route('/entrenar', methods=['GET', 'POST'])
def entrenar_modelo():
    """Ruta para entrenar el modelo desde la interfaz web"""
    if request.method == 'POST':
        try:
            # Importar el módulo de entrenamiento
            import train_bert
            
            # Crear ejemplos y entrenar el modelo
            ejemplos = train_bert.crear_ejemplos_adicionales()
            train_bert.guardar_ejemplos(ejemplos)
            
            # Número de épocas (por defecto 3)
            epochs = int(request.form.get('epochs', 3))
            
            # Entrenar el modelo
            train_bert.entrenar_modelo(epochs=epochs, ejemplos=ejemplos)
            
            # Recargar el modelo en el agente
            global agente_bert
            agente_bert = MundialesAgentBERT(api_url=os.getenv("API_BASE_URL", "http://localhost:3000/api"))
            
            return jsonify({
                'success': True,
                'message': f'Modelo entrenado exitosamente con {len(ejemplos)} ejemplos durante {epochs} épocas.'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Si es GET, mostrar página de entrenamiento
    return render_template('entrenar.html')

# Servir archivos estáticos de una manera organizada
@app.route('/static/<path:filename>')
def custom_static(filename):
    return app.send_static_file(filename)

# Configuración para ejecutar el servidor
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
