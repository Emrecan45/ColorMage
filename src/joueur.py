import pygame
import sys
from config import TAILLE_CELLULE, HAUTEUR_GRILLE, LARGEUR_GRILLE, COULEURS
from grille import obtenir_bloc, grille, traversables
from popup import afficher_popup

# ----- JOUEUR -----
couleur_joueur = "gris"
largeur_joueur = TAILLE_CELLULE
hauteur_joueur = TAILLE_CELLULE
joueur_x = 0
joueur_y = (HAUTEUR_GRILLE - 1) * TAILLE_CELLULE - hauteur_joueur
vitesse_x = 0
vitesse_y = 0
vitesse = 3
gravité = 0.5
force_saut = -10
au_sol = False

# Images du joueur
try:
    images_joueur = {
        "gris": pygame.image.load("../img/joueur_gris.png"),
        "rouge": pygame.image.load("../img/joueur_rouge.png"),
        "bleu": pygame.image.load("../img/joueur_bleu.png"),
        "vert": pygame.image.load("../img/joueur_vert.png")
    }
    # Redimensionner toutes les images
    for couleur in images_joueur:
        images_joueur[couleur] = pygame.transform.scale(images_joueur[couleur], (largeur_joueur, hauteur_joueur))
    utiliser_image = True
except:
    utiliser_image = False

# ----- FONCTIONS -----
def deplacer_joueur():
    global joueur_x, joueur_y, vitesse_x, vitesse_y, au_sol, couleur_joueur

    # Gravité
    vitesse_y += gravité
    nouveau_x = joueur_x + vitesse_x
    nouveau_y = joueur_y + vitesse_y

    # Empêcher de sortir de l'écran (murs invisibles)
    if nouveau_x < 0:
        nouveau_x = 0
        vitesse_x = 0
    if nouveau_x + largeur_joueur > LARGEUR_GRILLE * TAILLE_CELLULE:
        nouveau_x = LARGEUR_GRILLE * TAILLE_CELLULE - largeur_joueur
        vitesse_x = 0

    # Collision X
    if vitesse_x != 0:
        rect = pygame.Rect(nouveau_x, joueur_y, largeur_joueur, hauteur_joueur)
        if collision(rect):
            while not collision(pygame.Rect(joueur_x + (1 if vitesse_x > 0 else -1), joueur_y, largeur_joueur, hauteur_joueur)):
                joueur_x += (1 if vitesse_x > 0 else -1)
            vitesse_x = 0
        else:
            joueur_x = nouveau_x

    # Collision Y
    rect = pygame.Rect(joueur_x, nouveau_y, largeur_joueur, hauteur_joueur)
    if collision(rect):
        while not collision(pygame.Rect(joueur_x, joueur_y + (1 if vitesse_y > 0 else -1), largeur_joueur, hauteur_joueur)):
            joueur_y += (1 if vitesse_y > 0 else -1)
        if vitesse_y > 0:
            au_sol = True
        vitesse_y = 0
    else:
        joueur_y = nouveau_y
        au_sol = False

    # Interaction blocs
    bloc_x = int((joueur_x + largeur_joueur//2) / TAILLE_CELLULE)
    bloc_y = int((joueur_y + hauteur_joueur//2) / TAILLE_CELLULE)
    cible = obtenir_bloc(bloc_x, bloc_y)

    if cible == "change_rouge":
        couleur_joueur = "rouge"
        
    elif cible == "change_bleu":
        couleur_joueur = "bleu"
        
    elif cible == "change_vert":
        couleur_joueur = "vert"
        
    if cible == "porte":
        afficher_popup("Bravo, tu as gagné !")
        pygame.quit()
        sys.exit()
        
    if cible == "pic":
        afficher_popup("Game Over ! Vous êtes mort.")
        pygame.quit()
        sys.exit()

def collision(rect):
    for y in range(HAUTEUR_GRILLE):
        for x in range(LARGEUR_GRILLE):
            bloc = grille[y][x]
            if bloc not in traversables:
                if bloc == "noir" or bloc == "sol" or bloc != couleur_joueur:
                    bloc_rect = pygame.Rect(x*TAILLE_CELLULE, y*TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
    return False

def dessiner_joueur(ecran):
    if utiliser_image:
        ecran.blit(images_joueur[couleur_joueur], (joueur_x, joueur_y))
    else:
        pygame.draw.rect(ecran, COULEURS[couleur_joueur], (joueur_x, joueur_y, largeur_joueur, hauteur_joueur))
        pygame.draw.rect(ecran, (0, 0, 0), (joueur_x, joueur_y, largeur_joueur, hauteur_joueur), 2)