# Version du jeu
VERSION_JEU = "v1.2.0"

# Dimensions
TAILLE_CELLULE = 50
LARGEUR_GRILLE = 30
HAUTEUR_GRILLE = 15

LARGEUR_ECRAN = TAILLE_CELLULE * LARGEUR_GRILLE
HAUTEUR_ECRAN = TAILLE_CELLULE * HAUTEUR_GRILLE

# Couleurs
COULEURS = {
    "gris": (100, 100, 100),
    "rouge": (255, 0, 0),
    "bleu": (0, 0, 255),
    "vert": (0, 255, 0),
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
