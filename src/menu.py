import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU

class Menu:
    """Menu du jeu"""

    def __init__(self):
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)
        self.bouton_jouer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 80, 250, 50)
        self.bouton_parametres = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 60, 250, 50)
        self.bouton_quitter = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
    
    def afficher_menu(self, ecran):
        """Affiche le menu"""
        # Fond noir
        ecran.fill((0, 0, 0))
        
        # version du jeu
        version_txt = self.font_3.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))
        
        # titre du jeu
        titre_txt = self.font_1.render("ColorMage", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 220))
        
        # Dessiner les boutons
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_jouer)
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_parametres)
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_quitter)
        
        # Textes des boutons
        jouer_txt = self.font_2.render("Jouer", True, (255, 255, 255))
        parametres_txt = self.font_2.render("Paramètres", True, (255, 255, 255))
        quitter_txt = self.font_2.render("Quitter", True, (255, 255, 255))
        
        ecran.blit(jouer_txt, (LARGEUR_ECRAN // 2 - jouer_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 70))
        ecran.blit(parametres_txt, (LARGEUR_ECRAN // 2 - parametres_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 70))
        ecran.blit(quitter_txt, (LARGEUR_ECRAN // 2 - quitter_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 210))
        
        return None
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
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
