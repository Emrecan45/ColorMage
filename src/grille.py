import pygame
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS

# ----- GRILLE -----
grille = [["vide"] * LARGEUR_GRILLE for _ in range(HAUTEUR_GRILLE)]

# Création du sol
for x in range(LARGEUR_GRILLE):
    grille[HAUTEUR_GRILLE-1][x] = "sol"

# Blocs de couleur
grille[9][1] = "bleu"
grille[9][2] = "bleu"
grille[10][3] = "bleu"
grille[10][4] = "bleu"
grille[9][0] = "bleu"

grille[8][0] = "vert"
grille[8][1] = "vert"
grille[8][2] = "vert"
grille[7][3] = "vert"
grille[7][4] = "vert"
grille[13][4] = "vert"
grille[12][5] = "vert"
grille[11][6] = "vert"
grille[7][16] = "vert"
grille[7][17] = "vert"

grille[6][15] = "rouge"
grille[5][15] = "rouge"
grille[4][15] = "rouge"
grille[3][15] = "rouge"

grille[13][7] = "noir"
grille[12][7] = "noir"
grille[11][7] = "noir"
grille[10][7] = "noir"
grille[9][7] = "noir"
grille[8][7] = "noir"
grille[7][7] = "noir"
grille[7][8] = "noir"
grille[7][9] = "noir"
grille[7][10] = "noir"
grille[7][11] = "noir"
grille[7][12] = "noir"
grille[8][12] = "noir"
grille[9][12] = "noir"
grille[10][12] = "noir"
grille[11][12] = "noir"
grille[12][12] = "noir"
grille[13][12] = "noir"
grille[13][18] = "noir"
grille[12][18] = "noir"
grille[11][18] = "noir"
grille[10][18] = "noir"
grille[9][18] = "noir"
grille[8][18] = "noir"
grille[7][18] = "noir"
grille[7][19] = "noir"
grille[7][20] = "noir"
grille[7][21] = "noir"
grille[7][22] = "noir"

# Blocs change
grille[13][2] = "change_vert"
grille[6][1] = "change_vert"
grille[8][6] = "change_bleu"
grille[6][9] = "change_rouge"
grille[5][9] = "change_rouge"

# Pics
grille[13][13] = "pic"
grille[13][14] = "pic"
grille[13][15] = "pic"
grille[13][16] = "pic"
grille[13][17] = "pic"

# Porte
grille[HAUTEUR_GRILLE-2][LARGEUR_GRILLE-1] = "porte"

traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic"]
# Charger l'image du pic
image_pic = pygame.image.load("../img/pic.png")
image_pic = pygame.transform.scale(image_pic, (TAILLE_CELLULE, TAILLE_CELLULE))

# ----- FONCTIONS -----
def dessiner_grille(ecran):
    for y in range(HAUTEUR_GRILLE):
        for x in range(LARGEUR_GRILLE):
            if grille[y][x] == "pic":
                # Image du pic
                ecran.blit(image_pic, (x * TAILLE_CELLULE, y * TAILLE_CELLULE))
            elif "change" in grille[y][x]:
                # Cercle uniquement pour bloc change
                couleur = COULEURS[grille[y][x]]
                centre_x = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                centre_y = y * TAILLE_CELLULE + TAILLE_CELLULE // 2
                pygame.draw.circle(ecran, couleur, (centre_x, centre_y), TAILLE_CELLULE // 2 - 4)
            else:
                # Bloc normal : rectangle
                couleur = COULEURS[grille[y][x]]
                pygame.draw.rect(ecran, couleur, (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                if grille[y][x] != "vide":
                    pygame.draw.rect(ecran, (0, 0, 0), (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)

def obtenir_bloc(x, y):
    if 0 <= x < LARGEUR_GRILLE and 0 <= y < HAUTEUR_GRILLE:
        return grille[y][x]
    return "vide"