import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Menu:
    """Menu du jeu"""

    def __init__(self):
        self.font = pygame.font.SysFont(None, 50)
        self.bouton_jouer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 140, 250, 50)
        self.bouton_parametres = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 60, 250, 50)
        self.bouton_quitter = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20, 250, 50)
    
    def afficher_menu(self, ecran):
        """Affiche le menu et retourne l'action choisie
        
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou None si toujours dans le menu
        """
        # Fond noir
        ecran.fill((0, 0, 0))
        
        # Titre du jeu
        titre = self.font.render("ColorMage", True, (255, 255, 255))
        ecran.blit(titre, (LARGEUR_ECRAN // 2 - titre.get_width() // 2, HAUTEUR_ECRAN // 2 - 220))
        
        # Dessiner les boutons
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_jouer)
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_parametres)
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_quitter)
        
        # Textes des boutons
        jouer_txt = self.font.render("Jouer", True, (255, 255, 255))
        parametres_txt = self.font.render("Paramètres", True, (255, 255, 255))
        quitter_txt = self.font.render("Quitter", True, (255, 255, 255))
        
        ecran.blit(jouer_txt, (LARGEUR_ECRAN // 2 - jouer_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
        ecran.blit(parametres_txt, (LARGEUR_ECRAN // 2 - parametres_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 50))
        ecran.blit(quitter_txt, (LARGEUR_ECRAN // 2 - quitter_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 30))
        
        return None
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou None
        """
        if self.bouton_jouer.collidepoint(pos):
            return "jouer"
        elif self.bouton_parametres.collidepoint(pos):
            return "parametres"
        elif self.bouton_quitter.collidepoint(pos):
            return "quitter"
        return None
