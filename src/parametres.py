import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self):
        self.font = pygame.font.SysFont(None, 50)
        self.overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        self.overlay.fill((0, 0, 0))

    def afficher_parametres(self, ecran):
        ecran.blit(self.overlay, (0, 0))

        titre_txt = self.font.render("Parametres", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
        return None