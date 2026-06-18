import sys
import os

def resource_path(relative_path):
    """Retourne le chemin absolu vers une ressource, compatible avec PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Version du jeu
VERSION_JEU = "v2.2"

# Nombre de niveaux réellement disponibles
NIVEAUX_DISPONIBLES = 10

# Dimensions
TAILLE_CELLULE = 50
LARGEUR_GRILLE = 30
HAUTEUR_GRILLE = 17

LARGEUR_ECRAN = TAILLE_CELLULE * LARGEUR_GRILLE
HAUTEUR_ECRAN = TAILLE_CELLULE * HAUTEUR_GRILLE

# Couleurs
COULEURS = {
    "gris": (100, 100, 100),
    "rouge": (255, 0, 0),
    "bleu": (0, 0, 255),
    "vert": (41, 148, 45),
    "vide": (255, 255, 255),
    "porte": (255, 255, 0),
    "change_rouge": (255, 0, 0),
    "change_bleu": (0, 0, 255),
    "change_vert": (0, 255, 0),
    "noir": (0, 0, 0),
    "pic": (100, 100, 100)
}

COULEUR_BOUTON = (70, 70, 70)
COULEUR_SURVOL = (100, 100, 100)
COULEUR_BORDURE = (255, 255, 255)

GRAVITE = 0.75
VITESSE_DEPLACEMENT = 4.5
FORCE_SAUT = -15

# FPS
FPS = 60
