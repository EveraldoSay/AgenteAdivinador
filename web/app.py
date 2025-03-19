from flask import Flask, render_template, request, jsonify, session
from mundiales_akinator import MundialesAkinator
from mundiales_agent import MundialesAgent
from mundiales_agent_bert import MundialesAgentBERT
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf")
app.logger.setLevel(logging.DEBUG)

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
    try:
        datos = request.json
        modo = datos.get('modo', 'equipo')
        
        # Iniciar juego
        mensaje = akinator.iniciar_juego(modo)
        
        # Guardar estado en sesión de forma segura
        session['akinator_estado'] = serializable_estado(akinator.estado)
        
        # Generar primera pregunta
        pregunta = akinator.hacer_pregunta()
        
        return jsonify({
            'mensaje': mensaje,
            'pregunta': pregunta,
            'modo': modo
        })
    except Exception as e:
        app.logger.error(f"Error en iniciar_juego: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/responder', methods=['POST'])
def procesar_respuesta():
    try:
        datos = request.json
        respuesta = datos.get('respuesta', '')
        
        # Recuperar estado de la sesión
        if 'akinator_estado' in session:
            try:
                akinator.estado = session['akinator_estado']
            except Exception as e:
                app.logger.error(f"Error al recuperar estado: {e}")
                # Iniciar nuevo juego si hay problema con el estado
                modo = session.get('akinator_estado', {}).get('modo', 'equipo')
                akinator.iniciar_juego(modo)
        
        # Procesar respuesta
        resultado = akinator.procesar_respuesta(respuesta)
        
        # Guardar estado actualizado
        session['akinator_estado'] = serializable_estado(akinator.estado)
        
        # Determinar si es un resultado final o si necesita registro
        es_final = "¿Quieres jugar de nuevo?" in resultado or "¿Quieres intentar de nuevo?" in resultado
        necesita_registro = "No pude adivinar" in resultado or "No tengo más candidatos" in resultado
        
        return jsonify({
            'resultado': resultado,
            'es_final': es_final,
            'necesita_registro': necesita_registro,
            'modo': akinator.estado.get('modo', 'equipo')
        })
    except Exception as e:
        app.logger.error(f"Error en procesar_respuesta: {e}")
        return jsonify({
            'resultado': f"Ocurrió un error: {str(e)}",
            'es_final': True,
            'error': True
        }), 500

def serializable_estado(estado):
    """Convierte el estado en un objeto serializable para la sesión"""
    # Crea una copia limpia del estado
    estado_limpio = {}
    
    # Copia solo los elementos serializables
    for clave, valor in estado.items():
        if clave == "candidatos":
            # Para candidatos, solo mantener las propiedades básicas
            candidatos_limpios = []
            for candidato in valor:
                candidato_limpio = {
                    k: v for k, v in candidato.items() 
                    if isinstance(v, (str, int, float, bool, type(None)))
                }
                candidatos_limpios.append(candidato_limpio)
            estado_limpio[clave] = candidatos_limpios
        elif isinstance(valor, (str, int, float, bool, list, dict, type(None))):
            estado_limpio[clave] = valor
    
    return estado_limpio

@app.route('/api/posiciones', methods=['GET'])
def obtener_posiciones():
    """Obtiene la lista de posiciones disponibles"""
    try:
        # Asegurarse de que los datos estén cargados
        if not akinator.cache.get("posiciones"):
            akinator.cargar_datos()
        
        return jsonify(akinator.cache.get("posiciones", []))
    except Exception as e:
        app.logger.error(f"Error en obtener_posiciones: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/registrar/equipo', methods=['POST'])
def registrar_equipo():
    """Registra un nuevo equipo campeón"""
    try:
        datos = request.json
        
        pais = datos.get('pais', '')
        anio = datos.get('anio', '')
        
        if not pais or not anio:
            return jsonify({'success': False, 'error': 'Faltan datos obligatorios'}), 400
        
        # Verificar si ya existe
        existe = False
        for mundial in akinator.cache.get("mundiales", []):
            if mundial["pais"] == pais and str(mundial["anio"]) == str(anio):
                existe = True
                break
        
        if existe:
            return jsonify({'success': True, 'message': f'El mundial de {pais} en {anio} ya estaba registrado'})
        
        # Registrar nuevo mundial
        resultado = akinator.registrar_nuevo_equipo(pais, str(anio))
        
        if resultado:
            return jsonify({
                'success': True, 
                'message': f'Se ha registrado el mundial de {pais} en {anio}'
            })
        else:
            return jsonify({'success': False, 'error': 'Error al registrar el mundial'}), 500
    except Exception as e:
        app.logger.error(f"Error en registrar_equipo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/registrar/jugador', methods=['POST'])
def registrar_jugador():
    """Registra un nuevo jugador"""
    try:
        datos = request.json
        
        nombre = datos.get('nombre', '')
        pais = datos.get('pais', '')
        anio = datos.get('anio', '')
        posicion_id = datos.get('posicion_id')
        titular = datos.get('titular', False)
        
        if not nombre or not pais or not anio or posicion_id is None:
            return jsonify({'success': False, 'error': 'Faltan datos obligatorios'}), 400
        
        # Verificar si ya existe
        existe = False
        for jugador in akinator.cache.get("jugadores", []):
            if jugador["nombre"] == nombre and jugador["pais"] == pais and str(jugador["anio"]) == str(anio):
                existe = True
                break
        
        if existe:
            return jsonify({'success': True, 'message': f'El jugador {nombre} de {pais} en {anio} ya estaba registrado'})
        
        # Registrar jugador usando el método del akinator
        resultado = akinator.registrar_nuevo_jugador(nombre, pais, str(anio), posicion_id, titular)
        
        if resultado:
            # Obtener nombre de la posición
            posicion_nombre = "Desconocida"
            for pos in akinator.cache.get("posiciones", []):
                if pos["id"] == posicion_id:
                    posicion_nombre = pos["nombre"]
                    break
            
            return jsonify({
                'success': True,
                'message': f'Se ha registrado a {nombre}, {posicion_nombre} de {pais} en {anio}'
            })
        else:
            return jsonify({'success': False, 'error': 'Error al registrar el jugador'}), 500
    except Exception as e:
        app.logger.error(f"Error en registrar_jugador: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
