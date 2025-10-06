import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self):
        self.font = pygame.font.SysFont(None, 50)
        self.overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        self.overlay.fill((0, 0, 0))
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20, 250, 50)

    def afficher_parametres(self, ecran):
        """Affiche le menu et retourne l'action choisie
        
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou None si toujours dans le menu
        """
        #fond noir
        ecran.blit(self.overlay, (0, 0))
        
        #titre du menu
        titre_txt = self.font.render("Parametres", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
        
        #dessins des boutons
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        
        #textes dans les boutons
        retour_txt = self.font.render("Retour", True, (255, 255, 255))
        
        #affichage des textes dans les boutons
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 23))
          
        return None
    
        
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "quitter" ou None
        """
        if self.bouton_retour.collidepoint(pos):
            return "quitter"
        return None
