import torch
from transformers import BertTokenizer, BertForSequenceClassification
import re
import numpy as np
from typing import Dict, List, Any

class BERTProcessor:
    """
    Procesador de lenguaje natural utilizando modelos BERT para análisis
    de consultas relacionadas con datos de mundiales de fútbol.
    """
    
    def __init__(self, model_path=None):
        # Definir etiquetas de intención
        self.intent_labels = [
            "buscar_mundial_por_anio",
            "buscar_mundiales_por_pais",
            "buscar_jugador",
            "consultar_equipo_completo",
            "consulta_general"
        ]
        
        # Inicializar tokenizador BERT
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        
        # Inicializar modelo de clasificación
        if model_path and torch.cuda.is_available():
            # Cargar modelo pre-entrenado si está disponible
            self.model = BertForSequenceClassification.from_pretrained(
                'bert-base-multilingual-cased',
                num_labels=len(self.intent_labels)
            )
            self.model.load_state_dict(torch.load(model_path))
            self.model.to('cuda')
        else:
            # Usar modelo base si no hay uno pre-entrenado
            self.model = BertForSequenceClassification.from_pretrained(
                'bert-base-multilingual-cased',
                num_labels=len(self.intent_labels)
            )
        
        # Poner el modelo en modo evaluación
        self.model.eval()
        
        # Determinar dispositivo (CPU/GPU)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Utilizando dispositivo: {self.device}")
        
        # Lista de países para reconocimiento de entidades
        self.paises = [
            "brasil", "alemania", "italia", "argentina", 
            "francia", "españa", "inglaterra", "uruguay"
        ]
    
    def classify_intent(self, query: str) -> Dict[str, float]:
        """
        Clasifica la intención del usuario basada en su consulta
        """
        # Preparar entrada para BERT
        inputs = self.tokenizer(
            query,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        
        # Mover inputs al dispositivo apropiado
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Obtener predicciones
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
        # Convertir a probabilidades usando softmax
        probs = torch.nn.functional.softmax(logits, dim=1).squeeze().cpu().numpy()
        
        # Crear diccionario de intenciones y sus probabilidades
        intent_probs = {self.intent_labels[i]: float(probs[i]) for i in range(len(self.intent_labels))}
        
        return intent_probs
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extrae entidades como años, países y nombres de jugadores
        usando reglas simples y listas predefinidas
        """
        query = query.lower()
        entities = {
            "anio": None,
            "pais": None,
            "jugador": None
        }
        
        # Extraer año
        anio_match = re.search(r'\b(19\d\d|20\d\d)\b', query)
        if anio_match:
            entities["anio"] = int(anio_match.group(1))
        
        # Extraer país
        for pais in self.paises:
            if pais in query:
                entities["pais"] = pais.capitalize()
                break
        
        # Extraer posible jugador (esto es muy básico, se podría mejorar)
        # Aquí solo detectamos nombres propios que son capitalziados y no son países
        palabras = query.split()
        for palabra in palabras:
            if (len(palabra) > 3 and 
                palabra[0].isupper() and 
                palabra.lower() not in self.paises and
                palabra.lower() not in ["mundial", "copa", "mundo", "quien", "quién", "cuándo", "cuando"]):
                entities["jugador"] = palabra
                break
        
        return entities
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analiza una consulta y devuelve la intención y entidades detectadas
        """
        # Clasificar intención
        intent_probs = self.classify_intent(query)
        top_intent = max(intent_probs.items(), key=lambda x: x[1])[0]
        
        # Extraer entidades
        entities = self.extract_entities(query)
        
        # Devolver resultado del análisis
        return {
            "intent": top_intent,
            "intent_confidence": intent_probs[top_intent],
            "entities": entities,
            "all_intents": intent_probs
        }
    
    def fine_tune(self, training_data: List[Dict[str, str]], epochs: int = 3):
        """
        Realiza un fine-tuning del modelo con ejemplos específicos
        
        Args:
            training_data: Lista de diccionarios con 'texto' e 'intencion'
            epochs: Número de épocas de entrenamiento
        """
        # Configurar para entrenamiento
        self.model.train()
        
        # Preparar optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=5e-5)
        
        # Preparar datos
        texts = [item['texto'] for item in training_data]
        labels = [self.intent_labels.index(item['intencion']) for item in training_data]
        
        # Tokenizar
        encodings = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        )
        
        # Preparar dataset
        class IntentDataset(torch.utils.data.Dataset):
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels
                
            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item
            
            def __len__(self):
                return len(self.labels)
        
        dataset = IntentDataset(encodings, labels)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=8, shuffle=True)
        
        # Entrenamiento
        device = self.device
        self.model.to(device)
        
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()
                
                # Mover batch al dispositivo
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                # Backward pass
                loss.backward()
                optimizer.step()
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1}/{epochs} - Avg. Loss: {avg_loss:.4f}")
        
        # Guardar modelo entrenado
        torch.save(self.model.state_dict(), 'mundiales_bert_model.pt')
        print("Modelo guardado como: mundiales_bert_model.pt")
        
        # Volver a modo evaluación
        self.model.eval()
        
# Ejemplo de uso
if __name__ == "__main__":
    processor = BERTProcessor()
    
    # Ejemplos de consultas
    queries = [
        "¿Quién ganó el mundial de 1970?",
        "¿Cuántos mundiales ha ganado Brasil?",
        "¿Jugó Pelé en el mundial de 1958?",
        "¿Quiénes fueron los jugadores de Alemania en 2014?"
    ]
    
    for query in queries:
        analysis = processor.analyze_query(query)
        print(f"\nConsulta: {query}")
        print(f"Intención: {analysis['intent']} (confianza: {analysis['intent_confidence']:.2f})")
        print(f"Entidades: {analysis['entities']}")