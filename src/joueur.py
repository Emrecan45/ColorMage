import pygame
import json
from config import TAILLE_CELLULE, COULEURS, GRAVITE, VITESSE_DEPLACEMENT, FORCE_SAUT, LARGEUR_GRILLE, HAUTEUR_GRILLE
from config_manager import ConfigManager


class Joueur:
    """Le mage qui change de couleur"""
    
    def __init__(self, x, y):
        self.x_initial = x
        self.y_initial = y
        self.x = x
        self.y = y
        self.largeur = TAILLE_CELLULE
        self.hauteur = TAILLE_CELLULE
        self.couleur = "gris"
        
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
        
        # Chargement des touches
        self.gestionnaire_config = ConfigManager()
        self.controls = self.gestionnaire_config.obtenir_controles()

        # Chargement des images
        self.images = dict()
        
        img_gris = pygame.image.load("img/joueur_gris.png")
        self.images["gris"] = pygame.transform.scale(img_gris, (self.largeur, self.hauteur))

        img_rouge = pygame.image.load("img/joueur_rouge.png")
        self.images["rouge"] = pygame.transform.scale(img_rouge, (self.largeur, self.hauteur))

        img_bleu = pygame.image.load("img/joueur_bleu.png")
        self.images["bleu"] = pygame.transform.scale(img_bleu, (self.largeur, self.hauteur))

        img_verte = pygame.image.load("img/joueur_vert.png")
        self.images["vert"] = pygame.transform.scale(img_verte, (self.largeur, self.hauteur))
    
    def reset(self):
        """Réinitialise le joueur à sa position de départ et sa couleur de base (gris)"""
        self.x = self.x_initial
        self.y = self.y_initial
        self.couleur = "gris"
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
    
    def deplacer(self, touches, niveau):
        """Gère le déplacement du joueur"""
        #Entrées clavier
        self.vitesse_x = 0
        if self.controls['gauche'] != "":
            if touches[pygame.key.key_code(self.controls['gauche'])]:
                self.vitesse_x = -VITESSE_DEPLACEMENT

        if self.controls['droite'] != "":
            if touches[pygame.key.key_code(self.controls['droite'])]:
                self.vitesse_x = VITESSE_DEPLACEMENT

        if self.controls['sauter'] != "":
            if touches[pygame.key.key_code(self.controls['sauter'])] and self.au_sol:
                self.vitesse_y = FORCE_SAUT
                self.au_sol = False

        # Gravité
        self.vitesse_y += GRAVITE
        
        # Calcul nouvelles positions
        nouveau_x = self.x + self.vitesse_x
        nouveau_y = self.y + self.vitesse_y
        
        # Limites de l'ecran
        if nouveau_x < 0:
            nouveau_x = 0
            self.vitesse_x = 0
        if nouveau_x + self.largeur > LARGEUR_GRILLE * TAILLE_CELLULE:
            nouveau_x = LARGEUR_GRILLE * TAILLE_CELLULE - self.largeur
            self.vitesse_x = 0
        
        # Collision horizontale
        if self.vitesse_x != 0:
            rect = pygame.Rect(nouveau_x, self.y, self.largeur, self.hauteur)
            if niveau.collision(rect, self.couleur):
                while not niveau.collision(pygame.Rect(self.x + (1 if self.vitesse_x > 0 else -1), self.y, self.largeur, self.hauteur),self.couleur):
                    self.x += (1 if self.vitesse_x > 0 else -1)
                self.vitesse_x = 0
            else:
                self.x = nouveau_x
        
        # Collision verticale
        rect = pygame.Rect(self.x, nouveau_y, self.largeur, self.hauteur)
        if niveau.collision(rect, self.couleur):
            while not niveau.collision(pygame.Rect(self.x, self.y + (1 if self.vitesse_y > 0 else -1), self.largeur, self.hauteur),self.couleur):
                self.y += (1 if self.vitesse_y > 0 else -1)
            if self.vitesse_y > 0:
                self.au_sol = True
            self.vitesse_y = 0
        else:
            self.y = nouveau_y
            self.au_sol = False
    
    def interagir_avec_blocs(self, niveau):
        """Vérifie les interactions avec les blocs spéciaux"""
        bloc_x = int((self.x + self.largeur // 2) / TAILLE_CELLULE)
        bloc_y = int((self.y + self.hauteur // 2) / TAILLE_CELLULE)
        bloc = niveau.obtenir_bloc(bloc_x, bloc_y)
        
        if "change_" in bloc:
            nouvelle_couleur = bloc.split("change_")[1] # fait une liste ["change_", "couleur"] et on récupere [1] de cette liste
            self.couleur = nouvelle_couleur
        
        if bloc == "porte":
            return "victoire"
        
        if bloc == "pic":
            return "mort"
    
    def maj_controles(self):
        """Recharge les touches depuis le gestionnaire"""
        self.controls = self.gestionnaire_config.obtenir_controles()
    
    def dessiner(self, ecran):
        """Dessine le joueur"""
        if self.couleur in self.images:
            ecran.blit(self.images[self.couleur], (self.x, self.y))
