import json
import os
from core.config import resource_path

langue_actuelle = "en"
traductions = {}

def init(langue="en"):
    """Charge le fichier de langue correspondant."""
    global langue_actuelle, traductions
    langue_actuelle = langue
    
    chemin_fichier = resource_path(os.path.join("assets", "lang", f"{langue}.json"))
    
    if os.path.exists(chemin_fichier):
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                traductions = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la langue {langue}: {e}")
            traductions = {}
    else:
        print(f"Fichier de langue introuvable : {chemin_fichier}")
        traductions = {}

def t(cle, defaut=None):
    """Retourne le texte traduit pour une clé donnée.
    """
    if not traductions:
        return defaut if defaut is not None else cle
        
    parties = cle.split('.')
    courant = traductions
    
    for partie in parties:
        if isinstance(courant, dict) and partie in courant:
            courant = courant[partie]
        else:
            return defaut if defaut is not None else cle
            
    return courant
