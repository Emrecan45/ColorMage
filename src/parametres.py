import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self):
        self.largeur_bouton = 70
        self.hauteur_bouton = 70
        self.marge = 15
        self.image_pause = pygame.image.load("img/pause.png")
        self.image_pause = pygame.transform.scale(self.image_pause, (self.largeur_bouton, self.hauteur_bouton))
        
        # Coordonnées du bouton pause
        self.bouton_x = LARGEUR_ECRAN - self.largeur_bouton - self.marge
        self.bouton_y = self.marge
        self.bouton_rect = pygame.Rect(self.bouton_x, self.bouton_y, self.largeur_bouton, self.hauteur_bouton)
        
    def afficher_parametres(self, ecran):
        font = pygame.font.SysFont(None, 50)
        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        overlay.fill((0, 0, 0))
        ecran.blit(overlay, (0, 0))

        titre_txt = font.render("Parametres", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
        return None