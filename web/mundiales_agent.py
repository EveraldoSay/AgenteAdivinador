import requests
import json
import os
import re
from dotenv import load_dotenv
from typing import Dict, List, Any, Union, Optional

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000/api")

class MundialesAgent:
    """
    Agente para consultar información sobre los campeones de mundiales de fútbol
    """
    
    def __init__(self):
        self.api_url = API_BASE_URL
        self.cache = {
            "paises": None,
            "mundiales": None
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
    
    def get_paises(self, refresh: bool = False) -> List[Dict]:
        """
        Obtiene la lista de países campeones
        """
        if self.cache["paises"] is None or refresh:
            self.cache["paises"] = self._fetch_data("paises")
        return self.cache["paises"] or []
    
    def get_mundiales(self, refresh: bool = False) -> List[Dict]:
        """
        Obtiene la lista de mundiales
        """
        if self.cache["mundiales"] is None or refresh:
            self.cache["mundiales"] = self._fetch_data("mundiales")
        return self.cache["mundiales"] or []
    
    def get_mundial_detalle(self, mundial_id: int) -> Optional[Dict]:
        """
        Obtiene los detalles de un mundial específico
        """
        return self._fetch_data(f"mundiales/{mundial_id}")
    
    def buscar_jugador(self, nombre: str) -> List[Dict]:
        """
        Busca jugadores por nombre
        """
        if len(nombre) < 3:
            print("El nombre debe tener al menos 3 caracteres")
            return []
        
        return self._fetch_data(f"jugadores/buscar?q={nombre}") or []
    
    def get_mundial_por_anio_pais(self, anio: int = None, pais: str = None) -> Optional[Dict]:
        """
        Obtiene un mundial por año y/o país
        """
        mundiales = self.get_mundiales()
        
        if anio and pais:
            for mundial in mundiales:
                if mundial["anio"] == anio and mundial["pais"].upper() == pais.upper():
                    return self.get_mundial_detalle(mundial["id"])
        elif anio:
            for mundial in mundiales:
                if mundial["anio"] == anio:
                    return self.get_mundial_detalle(mundial["id"])
        elif pais:
            resultados = []
            for mundial in mundiales:
                if mundial["pais"].upper() == pais.upper():
                    resultados.append(self.get_mundial_detalle(mundial["id"]))
            return resultados
        
        return None
    
    def procesar_consulta(self, consulta: str) -> str:
        """
        Procesa una consulta en lenguaje natural y devuelve una respuesta
        """
        consulta = consulta.lower()
        
        # Buscar patrones específicos en la consulta
        
        # Patrón para consultar un año específico
        anio_match = re.search(r'\b(19\d\d|20\d\d)\b', consulta)
        anio = int(anio_match.group(1)) if anio_match else None
        
        # Buscar el nombre del país en la consulta
        paises = self.get_paises()
        pais_encontrado = None
        
        for pais in paises:
            if pais["nombre"].lower() in consulta:
                pais_encontrado = pais["nombre"]
                break
        
        # Diferentes tipos de consultas
        if "jugador" in consulta or "jugó" in consulta or "participó" in consulta:
            # Buscar un nombre de jugador (palabras con más de 3 letras que no sean palabras comunes)
            palabras = consulta.split()
            palabras_comunes = ["que","quien", "quién", "como", "cómo", "cuando", "cuándo", "donde", "dónde", 
                               "jugador", "jugó", "participó", "equipo", "mundial", "copa", "mundo", 
                               "selección", "ganó", "ganador", "campeón", "campeon"]
            
            nombres_potenciales = [palabra for palabra in palabras 
                                  if len(palabra) > 3 and palabra not in palabras_comunes]
            
            if nombres_potenciales:
                for nombre in nombres_potenciales:
                    resultados = self.buscar_jugador(nombre)
                    if resultados:
                        jugador = resultados[0]  # Tomamos el primer resultado
                        return f"{jugador['nombre']} jugó con {jugador['pais']} en el Mundial de {jugador['anio']} como {jugador['posicion']}. Era {'titular' if jugador['titular'] else 'suplente'}."
            
            return "No pude identificar a qué jugador te refieres."
        
        # Consulta sobre un mundial específico por año
        elif anio and ("mundial" in consulta or "copa" in consulta or "ganó" in consulta or "ganador" in consulta):
            mundial = self.get_mundial_por_anio_pais(anio=anio)
            if mundial:
                return f"El Mundial de {mundial['anio']} fue ganado por {mundial['pais']}."
            else:
                return f"No tengo información sobre el Mundial de {anio}."
        
        # Consulta sobre los mundiales ganados por un país
        elif pais_encontrado and ("mundial" in consulta or "copa" in consulta or "ganó" in consulta or "ganador" in consulta):
            mundiales = self.get_mundial_por_anio_pais(pais=pais_encontrado)
            if mundiales:
                if isinstance(mundiales, list):
                    anios = [str(m["anio"]) for m in mundiales]
                    return f"{pais_encontrado} ha ganado {len(anios)} Mundiales en los años: {', '.join(anios)}."
                else:
                    return f"{pais_encontrado} ganó el Mundial de {mundiales['anio']}."
            else:
                return f"No tengo información sobre mundiales ganados por {pais_encontrado}."
        
        # Consulta sobre un equipo específico (país y año)
        elif anio and pais_encontrado:
            mundial = self.get_mundial_por_anio_pais(anio=anio, pais=pais_encontrado)
            if mundial:
                titulares = mundial["jugadores"]["titulares"]
                titulares_str = ", ".join([f"{j['nombre']} ({j['posicion_abr']})" for j in titulares[:5]]) + "..."
                return f"El equipo de {mundial['pais']} que ganó el Mundial de {mundial['anio']} incluía a jugadores como: {titulares_str}"
            else:
                return f"{pais_encontrado} no ganó el Mundial de {anio} según mis datos."
        
        # Consulta general sobre mundiales
        elif "cuantos" in consulta or "cuántos" in consulta:
            if pais_encontrado:
                mundiales = self.get_mundial_por_anio_pais(pais=pais_encontrado)
                if mundiales:
                    return f"{pais_encontrado} ha ganado {len(mundiales)} Mundiales."
                else:
                    return f"No tengo información sobre mundiales ganados por {pais_encontrado}."
            else:
                mundiales = self.get_mundiales()
                return f"Tengo información sobre {len(mundiales)} Mundiales ganados por diferentes países."
        
        # Si no coincide con ningún patrón conocido
        return "No entiendo tu consulta. Puedes preguntar por un país específico, un año de Mundial, o un jugador."

    def chat(self):
        """
        Inicia un chat interactivo con el agente
        """
        print("¡Bienvenido al Agente de Mundiales!")
        print("Puedes preguntarme sobre equipos campeones del mundo, jugadores y más.")
        print("Escribe 'salir' para terminar.")
        
        while True:
            consulta = input("\nTu pregunta: ")
            if consulta.lower() in ["salir", "exit", "quit"]:
                print("¡Hasta luego!")
                break
                
            respuesta = self.procesar_consulta(consulta)
            print(f"\nAgente: {respuesta}")


if __name__ == "__main__":
    agente = MundialesAgent()
    agente.chat()