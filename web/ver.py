import torch

archivo = "mundiales_bert_model.pt"  # Reemplázalo con tu archivo
modelo = torch.load(archivo, map_location=torch.device("cpu"))
print(modelo)