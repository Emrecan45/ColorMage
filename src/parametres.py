import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self):
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)
        self.overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        self.overlay.fill((0, 0, 0))
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
        self.bouton_musique = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 90, 250, 15)
        self.bouton_general = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 0, 250, 15)
        self.jauge_musique = 50 # Valeur au debut de la jauge musique
        self.jauge_general = 50 # Valeur au debut de la jauge musique


    def afficher_parametres(self, ecran):
        """Affiche le menu et retourne l'action choisie
        
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou None si toujours dans le menu
        """
        # fond noir
        ecran.blit(self.overlay, (0, 0))
        
        # titre du menu
        titre_txt = self.font_1.render("Paramètres", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 220))
        
        # version du jeu
        version_txt = self.font_3.render("v1.0.0", True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))

        # volume musique
        musique_txt = self.font_3.render("Volume Musique", True, (255, 255, 255))
        ecran.blit(musique_txt, (LARGEUR_ECRAN // 2 - musique_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
        pygame.draw.rect(ecran, (100, 100, 100), self.bouton_musique)
        # remplissage de la jauge
        largeur_remplie = int((self.jauge_musique / 100) * self.bouton_musique.width)
        pygame.draw.rect(ecran, (0, 200, 0),(self.bouton_musique.x, self.bouton_musique.y, largeur_remplie, self.bouton_musique.height))

        # volume général
        general_txt = self.font_3.render("Volume général", True, (255, 255, 255))
        ecran.blit(general_txt, (LARGEUR_ECRAN // 2 - general_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 40))
        pygame.draw.rect(ecran, (100, 100, 100), self.bouton_general)
        # remplissage de la jauge
        largeur_remplie = int((self.jauge_general / 100) * self.bouton_general.width)
        pygame.draw.rect(ecran, (0, 200, 0),(self.bouton_general.x, self.bouton_general.y, largeur_remplie, self.bouton_general.height))
        
        # bouton retour
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 210))
          
        return None
    
        
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "quitter" ou "volume_musique_modifié" ou "volume_général_modifié" ou None
        """
        if self.bouton_retour.collidepoint(pos):
            return "quitter"
        if self.bouton_musique.collidepoint(pos):
            self.jauge_musique = int(((pos[0] - self.bouton_musique.x) / self.bouton_musique.width) * 100)
            return "volume_musique_modifié"
        if self.bouton_general.collidepoint(pos):
            self.jauge_general = int(((pos[0] - self.bouton_musique.x) / self.bouton_musique.width) * 100)
            return "volume_général_modifié"
        return None
