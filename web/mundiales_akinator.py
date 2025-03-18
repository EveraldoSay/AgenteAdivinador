# Modificación de mundiales_agent.py para funcionar como Akinator
import requests
import os
from typing import Dict, List, Any, Union, Optional
from dotenv import load_dotenv
import random
import re

# Cargar variables de entorno
load_dotenv()

class MundialesAkinator:
    """
    Agente tipo Akinator para adivinar equipos campeones del mundo
    """
    
    def __init__(self, api_url=None):
        # Configuración de la API
        self.api_url = api_url or os.getenv("API_BASE_URL", "http://localhost:3000/api")
        
        # Caché de datos
        self.cache = {
            "paises": None,
            "mundiales": None,
            "jugadores": None,
            "posiciones": None
        }
        
        # Estado del juego
        self.estado = {
            "modo": None,  # "equipo" o "jugador"
            "candidatos": [],
            "preguntas_hechas": [],
            "filtros": {},
            "intentos": 0,
            "max_intentos": 10,
            "ultima_pregunta": "",
            "ultimo_tipo": ""
        }
    
    def _fetch_data(self, endpoint: str) -> Union[Dict, List, None]:
        """
        Realiza una petición GET a la API
        """
        try:
            response = requests.get(f"{self.api_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {e}")
            return None
    
    def _post_data(self, endpoint: str, data: Dict) -> Union[Dict, None]:
        """
        Realiza una petición POST a la API
        """
        try:
            response = requests.post(f"{self.api_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar datos a la API: {e}")
            return None
    
    def cargar_datos(self):
        """
        Carga todos los datos necesarios para el juego
        """
        # Cargar países/equipos
        self.cache["paises"] = self._fetch_data("paises") or []
        
        # Cargar mundiales
        self.cache["mundiales"] = self._fetch_data("mundiales") or []
        
        # Cargar posiciones
        self.cache["posiciones"] = self._fetch_data("posiciones") or []
        
        # Cargar jugadores (esto podría ser bajo demanda según necesidad)
        self.cache["jugadores"] = []
        
        for mundial in self.cache["mundiales"]:
            detalles = self._fetch_data(f"mundiales/{mundial['id']}")
            if detalles and "jugadores" in detalles:
                for jugador in detalles["jugadores"].get("titulares", []) + detalles["jugadores"].get("suplentes", []):
                    # Asegurarse de que cada jugador tenga todas las claves necesarias
                    jugador_completo = {
                        "mundial_id": mundial["id"],
                        "anio": mundial["anio"],
                        "pais": mundial["pais"],
                        "nombre": jugador.get("nombre", "Jugador desconocido"),
                        "posicion": jugador.get("posicion", "Desconocida"),
                        "titular": jugador.get("titular", False),
                        "posicion_abr": jugador.get("posicion_abr", ""),
                        "posicion_id": jugador.get("posicion_id", None)
                    }
                    self.cache["jugadores"].append(jugador_completo)
        
        print(f"Datos cargados: {len(self.cache['paises'])} países, {len(self.cache['mundiales'])} mundiales, {len(self.cache['jugadores'])} jugadores")
        
        # Verificar que tenemos datos válidos para trabajar
        if not self.cache["jugadores"]:
            print("ADVERTENCIA: No se cargaron jugadores correctamente")
        else:
            print(f"Ejemplo de jugador cargado: {self.cache['jugadores'][0]}")
    
    def iniciar_juego(self, modo="equipo"):
        """
        Inicia un nuevo juego de adivinanzas
        
        Args:
            modo: "equipo" para adivinar equipos/mundiales, "jugador" para adivinar jugadores
        """
        if not self.cache["paises"]:
            self.cargar_datos()
        
        self.estado = {
            "modo": modo,
            "candidatos": [],
            "preguntas_hechas": [],
            "filtros": {},
            "intentos": 0,
            "max_intentos": 15 if modo == "jugador" else 8,
            "ultima_pregunta": "",
            "ultimo_tipo": ""
        }
        
        # Establecer candidatos iniciales según el modo
        if modo == "equipo":
            self.estado["candidatos"] = [m for m in self.cache["mundiales"]]
        else:  # modo == "jugador"
            self.estado["candidatos"] = [j for j in self.cache["jugadores"]]
        
        print(f"Juego iniciado en modo {modo} con {len(self.estado['candidatos'])} candidatos iniciales")
        
        # Devolver mensaje inicial
        if modo == "equipo":
            return "¡Piensa en un equipo campeón del mundo! Intentaré adivinarlo. Responde con 'sí', 'no' o 'no sé'."
        else:
            return "¡Piensa en un jugador campeón del mundo! Intentaré adivinarlo. Responde con 'sí', 'no' o 'no sé'."
    
    def hacer_pregunta(self) -> str:
        """
        Genera una pregunta estratégica para reducir los candidatos
        """
        modo = self.estado["modo"]
        candidatos = self.estado["candidatos"]
        self.estado["intentos"] += 1
        
        # Si no hay candidatos, rendirse
        if not candidatos:
            return "No tengo más candidatos. ¿Quieres intentar otra vez?"
        
        # Si quedan pocos candidatos o se alcanzó el máximo de intentos
        if len(candidatos) <= 2 or self.estado["intentos"] >= self.estado["max_intentos"]:
            candidato = candidatos[0]
            if modo == "equipo":
                return f"¿Estás pensando en {candidato['pais']} del Mundial {candidato['anio']}?"
            else:
                # Manejar de forma segura las posibles claves faltantes
                nombre = candidato.get('nombre', "Jugador desconocido")
                pais = candidato.get('pais', "país desconocido")
                anio = candidato.get('anio', "año desconocido")
                return f"¿Estás pensando en {nombre} que jugó con {pais} en {anio}?"
        
        # Generar preguntas según el modo
        if modo == "equipo":
            return self._generar_pregunta_equipo()
        else:
            return self._generar_pregunta_jugador()
    
    def _generar_pregunta_equipo(self) -> str:
        """
        Genera una pregunta sobre equipos/mundiales
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
        self.estado["ultimo_tipo"] = tipo_elegido
        
        # Formular pregunta según el tipo
        if tipo_elegido == "epoca":
            # Determinar punto medio de los años
            años = [c["anio"] for c in candidatos]
            año_medio = sorted(años)[len(años)//2]
            pregunta = f"¿El equipo ganó el mundial después del año {año_medio}?"
        
        elif tipo_elegido == "continente":
            # Preguntar por continente (simplificado)
            equipos_sudamericanos = ["Brasil", "Argentina", "Uruguay"]
            paises = set(c["pais"] for c in candidatos)
            if any(p in equipos_sudamericanos for p in paises):
                pregunta = "¿El equipo es de Sudamérica?"
            else:
                pregunta = "¿El equipo es de Europa?"
        
        elif tipo_elegido == "titulos":
            # Preguntar por cantidad de títulos
            paises_multiples = ["Brasil", "Alemania", "Italia"]
            paises = set(c["pais"] for c in candidatos)
            if any(p in paises_multiples for p in paises):
                pregunta = "¿El país ha ganado más de 2 mundiales?"
            else:
                pregunta = "¿El país ha ganado solo un mundial?"
        
        else:
            # Pregunta de respaldo
            equipos = list(set(c["pais"] for c in candidatos))
            equipo_aleatorio = random.choice(equipos)
            pregunta = f"¿El equipo es {equipo_aleatorio}?"
            self.estado["ultimo_tipo"] = "pais_directo"
        
        # Guardar la pregunta
        self.estado["ultima_pregunta"] = pregunta
        return pregunta
    
    def _generar_pregunta_jugador(self) -> str:
        """
        Genera una pregunta sobre jugadores
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
        
        # Filtrar los tipos ya preguntados (evitar repetir consecutivamente)
        tipos_disponibles = [t for t in tipos_preguntas if t != self.estado.get("ultimo_tipo", "")]
        if not tipos_disponibles:
            tipos_disponibles = tipos_preguntas
        
        # Elegir tipo de pregunta
        tipo_elegido = random.choice(tipos_disponibles)
        self.estado["ultimo_tipo"] = tipo_elegido
        
        # Formular pregunta según el tipo
        if tipo_elegido == "posicion":
            posiciones = [c.get("posicion", "Desconocida") for c in candidatos]
            posiciones_unicas = list(set(posiciones))
            
            if "Portero" in posiciones_unicas:
                pregunta = "¿El jugador es portero?"
            elif "Defensa" in posiciones_unicas:
                pregunta = "¿El jugador es defensa?"
            elif "Mediocampista" in posiciones_unicas:
                pregunta = "¿El jugador es mediocampista?"
            else:
                pregunta = "¿El jugador es delantero?"
        
        elif tipo_elegido == "epoca":
            # Determinar punto medio de los años
            años = [c.get("anio", 2000) for c in candidatos]
            año_medio = sorted(años)[len(años)//2]
            pregunta = f"¿El jugador ganó el mundial después del año {año_medio}?"
        
        elif tipo_elegido == "pais":
            paises = [c.get("pais", "Desconocido") for c in candidatos]
            paises_unicos = list(set(paises))
            if paises_unicos:
                pais_aleatorio = random.choice(paises_unicos)
                pregunta = f"¿El jugador es de {pais_aleatorio}?"
            else:
                pregunta = "¿El jugador es de Brasil?" # Pregunta por defecto
        
        elif tipo_elegido == "titular":
            titulares = [c for c in candidatos if c.get("titular", False)]
            if titulares and len(titulares) < len(candidatos):
                pregunta = "¿El jugador era titular?"
            else:
                pregunta = "¿El jugador era suplente?"
        
        else:
            # Si todo lo demás falla, hacer una pregunta sobre un jugador específico
            nombres = [c.get("nombre", "Desconocido") for c in candidatos if c.get("nombre") != "Jugador desconocido"]
            if nombres:
                jugador_aleatorio = random.choice(nombres)
                pregunta = f"¿El jugador es {jugador_aleatorio}?"
                self.estado["ultimo_tipo"] = "jugador_directo"
            else:
                pregunta = "¿El jugador ganó más de un mundial?"
                self.estado["ultimo_tipo"] = "multiple_campeon"
        
        # Guardar la pregunta
        self.estado["ultima_pregunta"] = pregunta
        return pregunta
    
    def procesar_respuesta(self, respuesta: str) -> str:
        """
        Procesa la respuesta del usuario y filtra los candidatos
        
        Args:
            respuesta: Respuesta del usuario ('sí', 'no', 'no sé')
            
        Returns:
            Siguiente pregunta o resultado
        """
        respuesta = respuesta.lower().strip()
        candidatos = self.estado["candidatos"]
        
        # Si no hay candidatos o se alcanzó el máximo de intentos
        if not candidatos or self.estado["intentos"] >= self.estado["max_intentos"]:
            # En lugar de manejar el fracaso directamente, indicamos que no pudimos adivinar
            return "No pude adivinar en qué estabas pensando. ¿Quieres intentar de nuevo?"
        
        # Si solo queda un candidato, verificar si hemos adivinado
        if len(candidatos) == 1:
            candidato = candidatos[0]
            if respuesta in ['sí', 'si', 's', 'yes', 'y']:
                if self.estado["modo"] == "equipo":
                    return f"¡Lo adiviné! Estabas pensando en {candidato['pais']} del Mundial {candidato['anio']}. ¿Quieres jugar de nuevo?"
                else:
                    nombre = candidato.get('nombre', "Jugador desconocido")
                    pais = candidato.get('pais', "país desconocido")
                    anio = candidato.get('anio', "año desconocido")
                    return f"¡Lo adiviné! Estabas pensando en {nombre} de {pais} ({anio}). ¿Quieres jugar de nuevo?"
            else:
                # No adivinamos, informar que necesitamos información
                return "No pude adivinar. ¿Quieres proporcionar los datos correctos?"
        
        # Filtrar candidatos según la respuesta y la última pregunta
        nuevos_candidatos = []
        tipo_pregunta = self.estado.get("ultimo_tipo", "")
        pregunta = self.estado.get("ultima_pregunta", "")
        
        # Si el usuario no sabe, no filtramos
        if respuesta in ['no sé', 'nose', 'no se', 'ns']:
            return self.hacer_pregunta()
        
        afirmativo = respuesta in ['sí', 'si', 's', 'yes', 'y']
        
        if self.estado["modo"] == "equipo":
            for candidato in candidatos:
                mantener = False
                
                if tipo_pregunta == "epoca":
                    año_pregunta = int(pregunta.split()[-1].rstrip("?"))
                    if (candidato["anio"] > año_pregunta and afirmativo) or (candidato["anio"] <= año_pregunta and not afirmativo):
                        mantener = True
                
                elif tipo_pregunta == "continente":
                    equipos_sudamericanos = ["Brasil", "Argentina", "Uruguay"]
                    es_sudamericano = candidato["pais"] in equipos_sudamericanos
                    es_pregunta_sudamericana = "sudamérica" in pregunta.lower()
                    
                    if (es_sudamericano and es_pregunta_sudamericana and afirmativo) or \
                       (not es_sudamericano and es_pregunta_sudamericana and not afirmativo) or \
                       (es_sudamericano and not es_pregunta_sudamericana and not afirmativo) or \
                       (not es_sudamericano and not es_pregunta_sudamericana and afirmativo):
                        mantener = True
                
                elif tipo_pregunta == "titulos":
                    paises_multiples = ["Brasil", "Alemania", "Italia"]
                    tiene_multiples = candidato["pais"] in paises_multiples
                    es_pregunta_multiples = "más de 2" in pregunta.lower()
                    
                    if (tiene_multiples and es_pregunta_multiples and afirmativo) or \
                       (not tiene_multiples and es_pregunta_multiples and not afirmativo) or \
                       (not tiene_multiples and not es_pregunta_multiples and afirmativo) or \
                       (tiene_multiples and not es_pregunta_multiples and not afirmativo):
                        mantener = True
                
                elif tipo_pregunta == "pais_directo":
                    pais_preguntado = pregunta.split("es ")[-1].rstrip("?")
                    if (candidato["pais"] == pais_preguntado and afirmativo) or \
                       (candidato["pais"] != pais_preguntado and not afirmativo):
                        mantener = True
                
                else:
                    # Si no entendemos la pregunta, mantenemos al candidato
                    mantener = True
                
                if mantener:
                    nuevos_candidatos.append(candidato)
        
        else:  # Modo jugador
            for candidato in candidatos:
                mantener = False
                
                if tipo_pregunta == "posicion":
                    posicion_candidato = candidato.get("posicion", "Desconocida")
                    es_portero = "portero" in pregunta.lower() and posicion_candidato == "Portero"
                    es_defensa = "defensa" in pregunta.lower() and posicion_candidato == "Defensa"
                    es_mediocampista = "mediocampista" in pregunta.lower() and posicion_candidato
                    
                elif tipo_pregunta == "epoca":
                    try:
                        año_pregunta = int(re.search(r'después del año (\d+)', pregunta).group(1))
                        if (candidato.get("anio", 0) > año_pregunta and afirmativo) or \
                           (candidato.get("anio", 0) <= año_pregunta and not afirmativo):
                            mantener = True
                    except (AttributeError, ValueError):
                        # Si hay error en el regex o conversión, mantenemos el candidato
                        mantener = True
                
                elif tipo_pregunta == "pais":
                    try:
                        pais_preguntado = pregunta.split("es de ")[-1].rstrip("?")
                        if (candidato.get("pais", "") == pais_preguntado and afirmativo) or \
                           (candidato.get("pais", "") != pais_preguntado and not afirmativo):
                            mantener = True
                    except:
                        mantener = True
                
                elif tipo_pregunta == "titular":
                    es_titular = candidato.get("titular", False)
                    es_pregunta_titular = "titular" in pregunta.lower()
                    
                    if (es_titular and es_pregunta_titular and afirmativo) or \
                       (not es_titular and not es_pregunta_titular and afirmativo) or \
                       (es_titular and es_pregunta_titular and not afirmativo) or \
                       (not es_titular and not es_pregunta_titular and not afirmativo):
                        mantener = True
                
                elif tipo_pregunta == "jugador_directo":
                    try:
                        nombre_preguntado = pregunta.split("es ")[-1].rstrip("?")
                        if (candidato.get("nombre", "") == nombre_preguntado and afirmativo) or \
                           (candidato.get("nombre", "") != nombre_preguntado and not afirmativo):
                            mantener = True
                    except:
                        mantener = True
                
                else:
                    # Si no entendemos la pregunta, mantenemos al candidato
                    mantener = True
                
                if mantener:
                    nuevos_candidatos.append(candidato)
        
        # Actualizar candidatos
        if nuevos_candidatos:
            self.estado["candidatos"] = nuevos_candidatos
            print(f"Candidatos restantes: {len(nuevos_candidatos)}")
        elif candidatos:  # Si no quedan candidatos pero teníamos algunos
            # Conservar algunos aleatoriamente para evitar quedarnos sin opciones
            self.estado["candidatos"] = random.sample(candidatos, max(1, min(3, len(candidatos))))
            print(f"Sin candidatos después del filtro, manteniendo {len(self.estado['candidatos'])} al azar")
        
        # Generar siguiente pregunta
        return self.hacer_pregunta()
    
    def registrar_nuevo_jugador(self, nombre: str, pais: str, anio: str, posicion_id: int, titular: bool) -> bool:
        """
        Registra un nuevo jugador en la base de datos
        """
        try:
            # Buscar o crear mundial
            mundial_id = None
            for mundial in self.cache.get("mundiales", []):
                if mundial["pais"] == pais and str(mundial["anio"]) == str(anio):
                    mundial_id = mundial["id"]
                    break
            
            if not mundial_id:
                # Crear nuevo mundial
                mundial_id = self._registrar_nuevo_mundial(pais, str(anio))
                if not mundial_id:
                    return False
            
            # Crear nuevo jugador
            nuevo_jugador = {
                "nombre": nombre,
                "mundial_id": mundial_id,
                "posicion_id": posicion_id,
                "titular": titular
            }
            
            resultado = self._post_data("jugadores", nuevo_jugador)
            if resultado:
                # Actualizar caché
                posicion_nombre = "Desconocida"
                for pos in self.cache.get("posiciones", []):
                    if pos["id"] == posicion_id:
                        posicion_nombre = pos["nombre"]
                        break
                    
                jugador_completo = {
                    "id": resultado.get("id"),
                    "nombre": nombre,
                    "mundial_id": mundial_id,
                    "anio": int(anio),
                    "pais": pais,
                    "posicion": posicion_nombre,
                    "posicion_id": posicion_id,
                    "titular": titular
                }
                self.cache["jugadores"].append(jugador_completo)
                return True
            
            return False
        except Exception as e:
            print(f"Error al registrar jugador: {e}")
            return False
    
    def _registrar_nuevo_mundial(self, pais: str, año: str) -> Optional[int]:
        """
        Registra un nuevo mundial y devuelve su ID
        """
        try:
            # Buscar o crear país
            pais_id = None
            for p in self.cache["paises"]:
                if p["nombre"] == pais:
                    pais_id = p["id"]
                    break
            
            if not pais_id:
                # Crear nuevo país
                nuevo_pais = {"nombre": pais}
                resultado = self._post_data("paises", nuevo_pais)
                if resultado:
                    pais_id = resultado.get("id")
                    print(f"País {pais} registrado correctamente.")
                    # Actualizar caché
                    self.cache["paises"].append(resultado)
                else:
                    print("Error al registrar el país.")
                    return None
            
            # Crear nuevo mundial
            nuevo_mundial = {
                "anio": int(año),
                "pais_id": pais_id
            }
            
            resultado = self._post_data("mundiales", nuevo_mundial)
            if resultado:
                # Actualizar caché
                resultado["pais"] = pais  # Añadir el nombre del país para facilitar el uso
                self.cache["mundiales"].append(resultado)
                return resultado.get("id")
            else:
                return None
        except Exception as e:
            print(f"Error al registrar mundial: {e}")
            return None
    
    def registrar_nuevo_equipo(self, pais: str, anio: str) -> bool:
        """
        Registra un nuevo equipo campeón en la base de datos
        """
        try:
            mundial_id = self._registrar_nuevo_mundial(pais, anio)
            return mundial_id is not None
        except Exception as e:
            print(f"Error al registrar equipo: {e}")
            return False
    
    def jugar(self):
        """
        Inicia el juego interactivo en consola
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
                    
