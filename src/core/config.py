import sys
import os

# True quand le jeu tourne dans le navigateur (compilé par pygbag en WebAssembly).
EST_WEB = sys.platform == "emscripten"


def detecter_mobile():
    """True sur un appareil tactile."""
    if not EST_WEB:
        return False
    try:
        import platform as plat
        return int(plat.window.navigator.maxTouchPoints) > 0
    except Exception:
        return False


EST_MOBILE = detecter_mobile()

etat_tactile = {"actif": EST_MOBILE}


def est_tactile():
    """True si le dernier mode d'entrée utilisé est le tactile."""
    return etat_tactile["actif"]


def set_tactile(valeur):
    """Met à jour le mode d'entrée (True = tactile, False = clavier)."""
    etat_tactile["actif"] = valeur


def resource_path(relative_path):
    """Retourne le chemin absolu vers une ressource, compatible avec PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Version du jeu
VERSION_JEU = "v2.4"

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
