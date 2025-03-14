import requests
import os
from typing import Dict, List, Any, Union, Optional
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()

class MundialesAkinator:
    """
    Agente tipo Akinator para adivinar equipos y jugadores campeones del mundo.
    """
    
    def __init__(self, api_url=None):
        # Configuración de la API
        self.api_url = api_url or os.getenv("API_BASE_URL", "http://localhost:3000/api")
        
        # Caché de datos
        self.cache = {
            "paises": None,
            "mundiales": None,
            "jugadores": None
        }
        
        # Estado del juego
        self.estado = {
            "modo": None,  # "equipo" o "jugador"
            "candidatos": [],
            "preguntas_hechas": [],
            "filtros": {},
            "intentos": 0,
            "max_intentos": 10  # Máximo de intentos antes de adivinar
        }
    
    def _fetch_data(self, endpoint: str) -> Union[Dict, List, None]:
        """
        Realiza una petición GET a la API.
        """
        try:
            response = requests.get(f"{self.api_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {e}")
            return None
    
    def cargar_datos(self):
        """
        Carga todos los datos necesarios para el juego.
        """
        # Cargar países/equipos
        self.cache["paises"] = self._fetch_data("paises") or []
        
        # Cargar mundiales
        self.cache["mundiales"] = self._fetch_data("mundiales") or []
        
        # Cargar jugadores
        self.cache["jugadores"] = []
        for mundial in self.cache["mundiales"]:
            detalles = self._fetch_data(f"mundiales/{mundial['id']}")
            if detalles and "jugadores" in detalles:
                for jugador in detalles["jugadores"].get("titulares", []) + detalles["jugadores"].get("suplentes", []):
                    jugador["mundial_id"] = mundial["id"]
                    jugador["anio"] = mundial["anio"]
                    jugador["pais"] = mundial["pais"]
                    self.cache["jugadores"].append(jugador)
    
    def iniciar_juego(self, modo="equipo"):
        """
        Inicia un nuevo juego de adivinanzas.
        
        Args:
            modo: "equipo" para adivinar equipos/mundiales, "jugador" para adivinar jugadores.
        """
        if not self.cache["paises"]:
            self.cargar_datos()
        
        self.estado = {
            "modo": modo,
            "candidatos": [],
            "preguntas_hechas": [],
            "filtros": {},
            "intentos": 0,
            "max_intentos": 15 if modo == "jugador" else 8
        }
        
        # Establecer candidatos iniciales según el modo
        if modo == "equipo":
            self.estado["candidatos"] = [m for m in self.cache["mundiales"]]
        else:  # modo == "jugador"
            self.estado["candidatos"] = [j for j in self.cache["jugadores"]]
        
        # Mensaje inicial
        if modo == "equipo":
            return "¡Piensa en un equipo campeón del mundo! Intentaré adivinarlo. Responde con 'sí', 'no' o 'no sé'."
        else:
            return "¡Piensa en un jugador campeón del mundo! Intentaré adivinarlo. Responde con 'sí', 'no' o 'no sé'."
    
    def hacer_pregunta(self) -> str:
        """
        Genera una pregunta estratégica para reducir los candidatos.
        """
        modo = self.estado["modo"]
        candidatos = self.estado["candidatos"]
        self.estado["intentos"] += 1
        
        # Si quedan pocos candidatos, intentar adivinar directamente
        if len(candidatos) <= 2 or self.estado["intentos"] >= self.estado["max_intentos"]:
            if candidatos:
                candidato = candidatos[0]
                if modo == "equipo":
                    return f"¿Estás pensando en {candidato['pais']} del Mundial {candidato['anio']}?"
                else:
                    return f"¿Estás pensando en {candidato['nombre']} que jugó con {candidato['pais']} en {candidato['anio']}?"
            else:
                return "¡Me rindo! No puedo adivinar en qué estabas pensando. ¿Quieres intentar otra vez?"
        
        # Generar preguntas según el modo
        if modo == "equipo":
            return self._generar_pregunta_equipo()
        else:
            return self._generar_pregunta_jugador()
    
    def _generar_pregunta_equipo(self) -> str:
        """
        Genera una pregunta sobre equipos/mundiales.
        """
        candidatos = self.estado["candidatos"]
        preguntas_hechas = self.estado["preguntas_hechas"]
        
        # Posibles tipos de preguntas
        tipos_preguntas = [
            "epoca",
            "continente",
            "titulos"
        ]
        
        # Filtrar los tipos ya preguntados
        tipos_disponibles = [t for t in tipos_preguntas if t not in preguntas_hechas]
        if not tipos_disponibles:
            tipos_disponibles = tipos_preguntas
        
        # Elegir tipo de pregunta aleatoriamente
        tipo_elegido = random.choice(tipos_disponibles)
        self.estado["preguntas_hechas"].append(tipo_elegido)
        
        # Formular pregunta según el tipo
        if tipo_elegido == "epoca":
            años = [c["anio"] for c in candidatos]
            año_medio = sorted(años)[len(años)//2]
            return f"¿El equipo ganó el mundial después del año {año_medio}?"
        
        elif tipo_elegido == "continente":
            equipos_sudamericanos = ["Brasil", "Argentina", "Uruguay"]
            paises = set(c["pais"] for c in candidatos)
            if any(p in equipos_sudamericanos for p in paises):
                return "¿El equipo es de Sudamérica?"
            else:
                return "¿El equipo es de Europa?"
        
        elif tipo_elegido == "titulos":
            paises_multiples = ["Brasil", "Alemania", "Italia"]
            paises = set(c["pais"] for c in candidatos)
            if any(p in paises_multiples for p in paises):
                return "¿El país ha ganado más de 2 mundiales?"
            else:
                return "¿El país ha ganado solo un mundial?"
        
        # Pregunta de respaldo
        equipos = list(set(c["pais"] for c in candidatos))
        equipo_aleatorio = random.choice(equipos)
        return f"¿El equipo es {equipo_aleatorio}?"
    
    def _generar_pregunta_jugador(self) -> str:
        """
        Genera una pregunta sobre jugadores.
        """
        candidatos = self.estado["candidatos"]
        preguntas_hechas = self.estado["preguntas_hechas"]
        
        # Posibles tipos de preguntas
        tipos_preguntas = [
            "posicion",
            "epoca",
            "pais",
            "titular"
        ]
        
        # Filtrar los tipos ya preguntados
        tipos_disponibles = [t for t in tipos_preguntas if t not in preguntas_hechas]
        if not tipos_disponibles:
            tipos_disponibles = tipos_preguntas
        
        # Elegir tipo de pregunta aleatoriamente
        tipo_elegido = random.choice(tipos_disponibles)
        self.estado["preguntas_hechas"].append(tipo_elegido)
        
        # Formular pregunta según el tipo
        if tipo_elegido == "posicion":
            posiciones = list(set(c["posicion"] for c in candidatos))
            if "Portero" in posiciones:
                return "¿El jugador es portero?"
            elif "Defensa" in posiciones:
                return "¿El jugador es defensa?"
            elif "Mediocampista" in posiciones:
                return "¿El jugador es mediocampista?"
            else:
                return "¿El jugador es delantero?"
        
        elif tipo_elegido == "epoca":
            años = [c["anio"] for c in candidatos]
            año_medio = sorted(años)[len(años)//2]
            return f"¿El jugador ganó el mundial después del año {año_medio}?"
        
        elif tipo_elegido == "pais":
            paises = list(set(c["pais"] for c in candidatos))
            pais_aleatorio = random.choice(paises)
            return f"¿El jugador es de {pais_aleatorio}?"
        
        elif tipo_elegido == "titular":
            titulares = [c for c in candidatos if c.get("titular", False)]
            if titulares:
                return "¿El jugador era titular?"
            else:
                return "¿El jugador era suplente?"
        
        # Pregunta de respaldo
        jugadores = list(set(c["nombre"] for c in candidatos))
        jugador_aleatorio = random.choice(jugadores)
        return f"¿El jugador es {jugador_aleatorio}?"
    
    def procesar_respuesta(self, respuesta: str) -> str:
        """
        Procesa la respuesta del usuario y filtra los candidatos.
        
        Args:
            respuesta: Respuesta del usuario ('sí', 'no', 'no sé').
            
        Returns:
            Siguiente pregunta o resultado.
        """
        respuesta = respuesta.lower().strip()
        candidatos = self.estado["candidatos"]
        
        # Si la lista de candidatos está vacía o hemos alcanzado el máximo de intentos
        if not candidatos or self.estado["intentos"] >= self.estado["max_intentos"]:
            return "No puedo adivinar en qué estabas pensando. ¿Quieres intentar de nuevo?"
        
        # Si solo queda un candidato, verificar si hemos adivinado
        if len(candidatos) == 1:
            candidato = candidatos[0]
            if respuesta in ['sí', 'si', 's', 'yes', 'y']:
                if self.estado["modo"] == "equipo":
                    return f"¡Lo adiviné! Estabas pensando en {candidato['pais']} del Mundial {candidato['anio']}. ¿Quieres jugar de nuevo?"
                else:
                    return f"¡Lo adiviné! Estabas pensando en {candidato['nombre']} de {candidato['pais']} ({candidato['anio']}). ¿Quieres jugar de nuevo?"
            else:
                return "¡Vaya! Me he equivocado. ¿Quieres intentar de nuevo?"
        
        # Procesar la respuesta para filtrar candidatos
        if respuesta in ['sí', 'si', 's', 'yes', 'y']:
            # Mantener aproximadamente el 60% de los candidatos
            self.estado["candidatos"] = random.sample(candidatos, max(1, int(len(candidatos) * 0.6)))
        elif respuesta in ['no', 'n']:
            # Mantener un 40% diferente
            self.estado["candidatos"] = random.sample(candidatos, max(1, int(len(candidatos) * 0.4)))
        
        # Generar siguiente pregunta
        return self.hacer_pregunta()
    
    def jugar(self):
        """
        Inicia el juego interactivo en consola.
        """
        print("¡Bienvenido al Akinator de Mundiales!")
        print("1. Adivinar equipo campeón")
        print("2. Adivinar jugador campeón")
        
        opcion = input("Elige una opción (1-2): ")
        
        if opcion == "1":
            modo = "equipo"
        else:
            modo = "jugador"
        
        mensaje = self.iniciar_juego(modo)
        print(mensaje)
        
        while True:
            pregunta = self.hacer_pregunta()
            print(f"\nPregunta: {pregunta}")
            
            if "¿Quieres jugar de nuevo?" in pregunta or "¿Quieres intentar de nuevo?" in pregunta:
                respuesta = input("Respuesta (sí/no): ")
                if respuesta.lower() in ['sí', 'si', 's', 'yes', 'y']:
                    mensaje = self.iniciar_juego(modo)
                    print(mensaje)
                else:
                    print("¡Gracias por jugar!")
                    break
            else:
                respuesta = input("Respuesta (sí/no/no sé): ")
                resultado = self.procesar_respuesta(respuesta)
                # La siguiente pregunta se mostrará en la próxima iteración

# Ejemplo de uso
if __name__ == "__main__":
    akinator = MundialesAkinator()
    akinator.jugar()