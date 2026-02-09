import pygame
import sys
import os
import random
import math
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE
from config_manager import ConfigManager

class Menu:
    """Menu du jeu"""

    def __init__(self):
        self.font_1 = pygame.font.SysFont(None, 50)
        self.font_2 = pygame.font.SysFont(None, 40)
        
        # Charger l'image de fond
        self.fond = pygame.image.load("img/fond_menu1.png")
        self.fond = pygame.transform.scale(self.fond, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        
        # Charger l'icône de profil (conserver les proportions)
        try:
            self.icone_profil = pygame.image.load("img/profile.png")
            # L'image fait 677x369, on garde les proportions pour 55px de haut
            ratio = self.icone_profil.get_width() / self.icone_profil.get_height()
            nouvelle_hauteur = 55
            nouvelle_largeur = int(nouvelle_hauteur * ratio)
            self.icone_profil = pygame.transform.smoothscale(self.icone_profil, (nouvelle_largeur, nouvelle_hauteur))
        except:
            self.icone_profil = None
        
        self.bouton_jouer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 60, 250, 50)
        self.bouton_grimoire = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20, 250, 50)
        self.bouton_parametres = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 100, 250, 50)
        self.bouton_quitter = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 180, 250, 50)
        self.bouton_profil = pygame.Rect(LARGEUR_ECRAN - 100, 15, 80, 80)
        
        # son des clics
        self.gestionnaire_config = ConfigManager()
        self.son_select = pygame.mixer.Sound(os.path.join("audio", "select.mp3"))
        self.maj_volume()
    
    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
    
    def dessiner_bouton_arrondi(self, ecran, rect, couleur, texte, font):
        """Dessine un bouton avec des bords arrondis"""
        pygame.draw.rect(ecran, couleur, rect, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, rect, 3, border_radius=10)
        
        texte_surface = font.render(texte, True, (255, 255, 255))
        ecran.blit(texte_surface, (rect.centerx - texte_surface.get_width() // 2,
                                  rect.centery - texte_surface.get_height() // 2))
    
    def afficher_menu(self, ecran):
        """Affiche le menu"""
        # Mettre à jour le volume à chaque affichage
        self.maj_volume()
        
        # Afficher l'image de fond
        ecran.blit(self.fond, (0, 0))
        
        # version du jeu
        version_txt = self.font_2.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))
        
        # Dessiner les boutons avec bords arrondis
        mouse_pos = pygame.mouse.get_pos()
        
        # Bouton Jouer
        couleur_jouer = COULEUR_SURVOL if self.bouton_jouer.collidepoint(mouse_pos) else COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_jouer, couleur_jouer, "Jouer", self.font_1)
        
        # Bouton Grimoire
        couleur_grimoire = COULEUR_SURVOL if self.bouton_grimoire.collidepoint(mouse_pos) else COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_grimoire, couleur_grimoire, "Grimoire", self.font_1)
        
        # Bouton Paramètres
        couleur_param = COULEUR_SURVOL if self.bouton_parametres.collidepoint(mouse_pos) else COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_parametres, couleur_param, "Paramètres", self.font_1)
        
        # Bouton Quitter
        couleur_quitter = COULEUR_SURVOL if self.bouton_quitter.collidepoint(mouse_pos) else COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_quitter, couleur_quitter, "Quitter", self.font_1)
        
        # Bouton Profil (en haut à droite avec icône)
        couleur_profil = COULEUR_SURVOL if self.bouton_profil.collidepoint(mouse_pos) else COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur_profil, self.bouton_profil, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_profil, 2, border_radius=10)
        if self.icone_profil:
            icone_x = self.bouton_profil.centerx - self.icone_profil.get_width() // 2
            icone_y = self.bouton_profil.centery - self.icone_profil.get_height() // 2
            ecran.blit(self.icone_profil, (icone_x, icone_y))
        
        return None
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou "profil" ou None
        """
        if self.bouton_profil.collidepoint(pos):
            self.son_select.play()
            return "profil"
        if self.bouton_jouer.collidepoint(pos):
            self.son_select.play()
            return "jouer"
        elif self.bouton_grimoire.collidepoint(pos):
            self.son_select.play()
            return "grimoire"
        elif self.bouton_parametres.collidepoint(pos):
            self.son_select.play()
            return "parametres"
        elif self.bouton_quitter.collidepoint(pos):
            self.son_select.play()
            pygame.time.wait(500) # pour que le son_select s'entende
            return "quitter"
        return None
