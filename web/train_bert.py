"""
Script para entrenar el modelo BERT con ejemplos específicos del dominio
de mundiales de fútbol.

Este entrenamiento mejora la capacidad del modelo para entender consultas
relacionadas con equipos campeones, jugadores y años de mundiales.
"""

import os
import json
from mundiales_agent_bert import MundialesAgentBERT

def crear_ejemplos_adicionales():
    """
    Crea un conjunto más amplio de ejemplos para entrenar el modelo
    """
    ejemplos = [
        # Ejemplos para buscar_mundial_por_anio
        {"texto": "¿Quién ganó el mundial de 1970?", "intencion": "buscar_mundial_por_anio"},
        {"texto": "¿Qué país fue campeón en 1990?", "intencion": "buscar_mundial_por_anio"},
        {"texto": "¿Quién ganó la copa del mundo en 2010?", "intencion": "buscar_mundial_por_anio"},
        {"texto": "Campeón del mundial 1966", "intencion": "buscar_mundial_por_anio"},
        {"texto": "¿Qué equipo ganó en 1982?", "intencion": "buscar_mundial_por_anio"},
        {"texto": "Ganador de la Copa Mundial 2014", "intencion": "buscar_mundial_por_anio"},
        {"texto": "Mundial 2006 campeón", "intencion": "buscar_mundial_por_anio"},
        {"texto": "¿Quién levantó la copa en 1998?", "intencion": "buscar_mundial_por_anio"},
        
        # Ejemplos para buscar_mundiales_por_pais
        {"texto": "¿Cuántos mundiales ha ganado Brasil?", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "Mundiales ganados por Alemania", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "Títulos mundiales de Argentina", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "¿En qué años fue campeón Italia?", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "¿Cuántas copas del mundo tiene Francia?", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "¿España ha ganado algún mundial?", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "Historial de títulos de Inglaterra", "intencion": "buscar_mundiales_por_pais"},
        {"texto": "¿Cuándo fue campeón Brasil por última vez?", "intencion": "buscar_mundiales_por_pais"},
        
        # Ejemplos para buscar_jugador
        {"texto": "¿Pelé jugó en el mundial de 1958?", "intencion": "buscar_jugador"},
        {"texto": "¿Maradona fue campeón en qué año?", "intencion": "buscar_jugador"},
        {"texto": "¿En qué posición jugaba Ronaldo en 2002?", "intencion": "buscar_jugador"},
        {"texto": "¿Messi jugó la final de 2022?", "intencion": "buscar_jugador"},
        {"texto": "¿Beckenbauer fue parte del equipo de 1974?", "intencion": "buscar_jugador"},
        {"texto": "¿Fue Zidane titular en 1998?", "intencion": "buscar_jugador"},
        {"texto": "Información sobre Iniesta en 2010", "intencion": "buscar_jugador"},
        {"texto": "¿En qué mundiales jugó Buffon?", "intencion": "buscar_jugador"},
        
        # Ejemplos para consultar_equipo_completo
        {"texto": "¿Quiénes fueron los jugadores de Alemania en 2014?", "intencion": "consultar_equipo_completo"},
        {"texto": "Alineación de Brasil 1970", "intencion": "consultar_equipo_completo"},
        {"texto": "Plantilla de España 2010", "intencion": "consultar_equipo_completo"},
        {"texto": "Equipo de Argentina 2022", "intencion": "consultar_equipo_completo"},
        {"texto": "¿Cuál fue el 11 titular de Italia en 2006?", "intencion": "consultar_equipo_completo"},
        {"texto": "Jugadores de Francia 2018", "intencion": "consultar_equipo_completo"},
        {"texto": "Muéstrame la plantilla de Brasil 1994", "intencion": "consultar_equipo_completo"},
        {"texto": "Formación de Alemania 1954", "intencion": "consultar_equipo_completo"},
        
        # Ejemplos para consulta_general
        {"texto": "Háblame de los mundiales de fútbol", "intencion": "consulta_general"},
        {"texto": "¿Cuántos mundiales hay en la base de datos?", "intencion": "consulta_general"},
        {"texto": "¿Qué países han ganado más mundiales?", "intencion": "consulta_general"},
        {"texto": "Información sobre campeones del mundo", "intencion": "consulta_general"},
        {"texto": "¿Qué puedo preguntarte sobre los mundiales?", "intencion": "consulta_general"},
        {"texto": "Datos curiosos de las copas del mundo", "intencion": "consulta_general"},
        {"texto": "¿Cuál es el país más ganador?", "intencion": "consulta_general"},
        {"texto": "Resumen de mundiales", "intencion": "consulta_general"}
    ]
    
    return ejemplos

def guardar_ejemplos(ejemplos, filename="ejemplos_entrenamiento.json"):
    """
    Guarda los ejemplos de entrenamiento en un archivo JSON
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ejemplos, f, ensure_ascii=False, indent=2)
    
    print(f"Ejemplos guardados en {filename}")

def cargar_ejemplos(filename="ejemplos_entrenamiento.json"):
    """
    Carga ejemplos de entrenamiento desde un archivo JSON
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            ejemplos = json.load(f)
        print(f"Cargados {len(ejemplos)} ejemplos desde {filename}")
        return ejemplos
    else:
        print(f"No se encontró el archivo {filename}")
        return None

def entrenar_modelo(epochs=5, ejemplos=None):
    """
    Entrena el modelo BERT con los ejemplos proporcionados
    """
    # Si no se proporcionan ejemplos, usar los predeterminados
    if ejemplos is None:
        ejemplos = crear_ejemplos_adicionales()
    
    # Crear el agente
    agente = MundialesAgentBERT()
    
    # Sobreescribir los ejemplos de entrenamiento
    agente.training_examples = ejemplos
    
    # Entrenar el modelo
    print(f"Iniciando entrenamiento con {len(ejemplos)} ejemplos durante {epochs} épocas...")
    agente.entrenar_modelo(epochs=epochs)
    
    print("Entrenamiento completado. Modelo guardado como 'mundiales_bert_model.pt'")
    
    return agente

def evaluar_modelo(agente, consultas_prueba):
    """
    Evalúa el rendimiento del modelo con consultas de prueba
    """
    print("\n=== EVALUACIÓN DEL MODELO ===\n")
    
    for consulta in consultas_prueba:
        print(f"Consulta: {consulta}")
        analisis = agente.nlp.analyze_query(consulta)
        
        print(f"Intención detectada: {analisis['intent']} (confianza: {analisis['intent_confidence']:.2f})")
        print(f"Entidades: {analisis['entities']}")
        
        respuesta = agente.procesar_consulta(consulta)
        print(f"Respuesta: {respuesta}\n")
        print("-" * 50)

if __name__ == "__main__":
    # Crear ejemplos y guardarlos
    ejemplos = crear_ejemplos_adicionales()
    guardar_ejemplos(ejemplos)
    
    # Preguntar si se desea entrenar el modelo
    respuesta = input("¿Deseas entrenar el modelo BERT ahora? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        # Número de épocas
        try:
            epochs = int(input("Número de épocas para el entrenamiento (recomendado 3-5): "))
        except ValueError:
            epochs = 3
            print(f"Valor no válido, usando {epochs} épocas por defecto.")
        
        # Entrenar el modelo
        agente = entrenar_modelo(epochs=epochs, ejemplos=ejemplos)
        
        # Consultas de prueba para evaluar el modelo
        consultas_prueba = [
            "¿Quién ganó el mundial de 1986?",
            "¿Cuántos mundiales tiene Alemania?",
            "¿Jugó Zidane en el equipo de Francia 1998?",
            "Muéstrame el equipo de Brasil del 70",
            "¿Qué países han sido campeones?"
        ]
        
        # Evaluar el modelo
        evaluar_modelo(agente, consultas_prueba)
        
        # Iniciar chat interactivo
        iniciar_chat = input("¿Deseas iniciar un chat interactivo con el agente? (s/n): ")
        if iniciar_chat.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            agente.chat()
    else:
        print("Entrenamiento cancelado.")