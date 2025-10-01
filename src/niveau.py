import pygame
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self):
        self.grille = []
        self.traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic"]
        self.image_pic = pygame.image.load("img/pic.png")
        self.image_pic = pygame.transform.scale(self.image_pic, (TAILLE_CELLULE, TAILLE_CELLULE))
    
    def creer_grille_niveau_1(self):
        """Crée la grille du niveau 1"""
        self.grille = []
        for b in range(HAUTEUR_GRILLE):
            ligne = []
            for a in range(LARGEUR_GRILLE):
                ligne.append("vide")
            self.grille.append(ligne)
        
        # sol
        for i in range(LARGEUR_GRILLE):
            self.grille[14][i] = "noir"

        # Blocs bleus
        self.grille[9][0] = "bleu"
        self.grille[9][1] = "bleu"
        self.grille[9][2] = "bleu"
        self.grille[10][3] = "bleu"
        self.grille[10][4] = "bleu"

        # Blocs verts
        self.grille[8][0] = "vert"
        self.grille[8][1] = "vert"
        self.grille[8][2] = "vert"
        self.grille[7][3] = "vert"
        self.grille[7][4] = "vert"
        self.grille[13][4] = "vert"
        self.grille[12][5] = "vert"
        self.grille[11][6] = "vert"
        self.grille[7][16] = "vert"
        self.grille[7][17] = "vert"

        # Blocs rouges
        self.grille[6][15] = "rouge"
        self.grille[5][15] = "rouge"
        self.grille[4][15] = "rouge"
        self.grille[3][15] = "rouge"

        # Murs
        self.grille[13][7] = "noir"
        self.grille[12][7] = "noir"
        self.grille[11][7] = "noir"
        self.grille[10][7] = "noir"
        self.grille[9][7] = "noir"
        self.grille[8][7] = "noir"
        self.grille[7][7] = "noir"
        self.grille[7][8] = "noir"
        self.grille[7][9] = "noir"
        self.grille[7][10] = "noir"
        self.grille[7][11] = "noir"
        self.grille[7][12] = "noir"
        self.grille[8][12] = "noir"
        self.grille[9][12] = "noir"
        self.grille[10][12] = "noir"
        self.grille[11][12] = "noir"
        self.grille[12][12] = "noir"
        self.grille[13][12] = "noir"
        self.grille[13][18] = "noir"
        self.grille[12][18] = "noir"
        self.grille[11][18] = "noir"
        self.grille[10][18] = "noir"
        self.grille[9][18] = "noir"
        self.grille[8][18] = "noir"
        self.grille[7][18] = "noir"
        self.grille[7][19] = "noir"
        self.grille[7][20] = "noir"
        self.grille[7][21] = "noir"
        self.grille[7][22] = "noir"

        # Portails de changement de couleur
        self.grille[13][2] = "change_vert"
        self.grille[6][1] = "change_vert"
        self.grille[8][6] = "change_bleu"
        self.grille[6][9] = "change_rouge"
        self.grille[5][9] = "change_rouge"

        # Pics
        self.grille[13][13] = "pic"
        self.grille[13][14] = "pic"
        self.grille[13][15] = "pic"
        self.grille[13][16] = "pic"
        self.grille[13][17] = "pic"

        # Porte de sortie
        self.grille[13][29] = "porte"

        return self.grille

    
    def charger_niveau_1(self):
        """Charge le premier niveau"""
        self.grille = self.creer_grille_niveau_1()
    
    def reset(self):
        """Réinitialise le niveau"""
        self.charger_niveau_1()
    
    def obtenir_bloc(self, x, y):
        """Retourne le type de bloc à une position donnée"""
        if 0 <= x < LARGEUR_GRILLE and 0 <= y < HAUTEUR_GRILLE:
            return self.grille[y][x]
        return "vide"
    
    def collision(self, rect, couleur_joueur):
        """Vérifie si un rectangle entre en collision avec un bloc solide"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                # Blocs toujours solides
                if bloc == "noir":
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
                
                # Blocs de couleur (solides seulement si même couleur)
                elif bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
        
        return False
    
    def dessiner(self, ecran):
        """Dessine tous les blocs du niveau"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                if bloc == "pic" and self.image_pic:
                    ecran.blit(self.image_pic, (x * TAILLE_CELLULE, y * TAILLE_CELLULE))
                
                elif bloc.startswith("change_"):
                    # Portails = cercles colorés
                    couleur = COULEURS[bloc]
                    centre_x = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    centre_y = y * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    pygame.draw.circle(ecran, couleur, (centre_x, centre_y), TAILLE_CELLULE // 2 - 4)
                
                else:
                    # Blocs normaux
                    couleur = COULEURS[bloc]
                    pygame.draw.rect(ecran, couleur, (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    if bloc != "vide":
                        pygame.draw.rect(ecran, (0, 0, 0), (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
