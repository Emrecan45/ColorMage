import pygame
import os
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN
from config_manager import ConfigManager
from chronometre import Chronometre

class Popup:
    """Gère l'affichage des popups de victoire et de défaite"""

    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        
        # son des clics
        self.gestionnaire_config = ConfigManager()
        self.son_select = pygame.mixer.Sound(os.path.join("audio", "select.mp3"))
        
        self.largeur_popup = 600
        self.hauteur_popup = 400
        
        # Rectangle du popup
        self.popup_rect = pygame.Rect(
            (LARGEUR_ECRAN - self.largeur_popup) // 2,
            (HAUTEUR_ECRAN - self.hauteur_popup) // 2,
            self.largeur_popup,
            self.hauteur_popup
        )
        
        # Créer les boutons (positionnés verticalement)
        self.bouton_suivant = pygame.Rect(0, 0, 260, 60)
        self.bouton_suivant.center = (self.popup_rect.centerx, self.popup_rect.top + 160)
        
        self.bouton_recommencer = pygame.Rect(0, 0, 260, 60)
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 250)
        
        self.bouton_quitter = pygame.Rect(0, 0, 260, 60)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 340)

    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_select.set_volume(volumes.get("effets", 50) / 100)

    def niveau_existe(self, numero_niveau):
        """Vérifie si un fichier de niveau existe"""
        chemin = "niveaux/niveau_" + str(numero_niveau) + ".json"
        try:
            with open(chemin, "r") as f:
                pass
            return True
        except:
            return False

    def gerer_clic_victoire(self, pos, niveau_actuel):
        """Gère les clics pour le popup de victoire
        
        Args:
            pos: Position du clic (x, y)
            niveau_actuel: Numéro du niveau actuel
            
        Returns:
            str: "suivant", "rejouer", "quitter" ou None
        """
        # Vérifier si le niveau suivant existe pour activer le bouton
        if self.niveau_existe(niveau_actuel + 1):
            if self.bouton_suivant.collidepoint(pos):
                self.son_select.play()
                return "suivant"
        
        if self.bouton_recommencer.collidepoint(pos):
            self.son_select.play()
            return "rejouer"

        elif self.bouton_quitter.collidepoint(pos):
            self.son_select.play()
            return "quitter"
        return None
    
    def gerer_clic_defaite(self, pos):
        """Gère les clics pour le popup de défaite
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "rejouer", "quitter" ou None
        """
        if self.bouton_recommencer.collidepoint(pos):
            self.son_select.play()
            return "rejouer"
        elif self.bouton_quitter.collidepoint(pos):
            self.son_select.play()
            return "quitter"
        return None

    def dessiner_popup_victoire(self, ecran, niveau_actuel, temps_ms=0):
        """Dessine le popup de victoire avec le temps"""
        self.maj_volume()
        
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)

        # Titre
        titre_surface = self.font.render("Bravo ! Niveau terminé", True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 50
        ecran.blit(titre_surface, (titre_x, titre_y))
        
        #afficher le temps
        if temps_ms > 0:
            temps_texte = "Temps : " + str(Chronometre.formater_temps(self, temps_ms))
            font_temps = pygame.font.Font(None, 40)
            temps_surface = font_temps.render(temps_texte, True, (0, 100, 0))
            temps_x = self.popup_rect.x + (self.popup_rect.width - temps_surface.get_width()) // 2
            temps_y = self.popup_rect.y + 100
            ecran.blit(temps_surface, (temps_x, temps_y))

        # Liste des boutons avec leurs textes
        boutons = []
        
        # Ajouter le bouton "Niveau suivant" seulement s'il existe
        if self.niveau_existe(niveau_actuel + 1):
            boutons.append((self.bouton_suivant, "Niveau suivant"))
        
        # Ajuster la position du bouton recommencer selon s'il y a un bouton suivant
        if self.niveau_existe(niveau_actuel + 1):
            self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 250)
        else:
            self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 200)
        
        boutons.append((self.bouton_recommencer, "Recommencer"))
        
        # Ajuster la position du bouton quitter
        if self.niveau_existe(niveau_actuel + 1):
            self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 340)
        else:
            self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 290)
        
        boutons.append((self.bouton_quitter, "Quitter"))

        # Dessiner les boutons
        for rect, texte in boutons:
            # Effet de survol
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, (200, 200, 200), rect)
            else:
                pygame.draw.rect(ecran, (230, 230, 230), rect)

            # Bordure du bouton
            pygame.draw.rect(ecran, (0, 0, 0), rect, 3)

            # Texte du bouton
            texte_surface = self.font.render(texte, True, (0, 0, 0))
            texte_x = rect.x + (rect.width - texte_surface.get_width()) // 2
            texte_y = rect.y + (rect.height - texte_surface.get_height()) // 2
            ecran.blit(texte_surface, (texte_x, texte_y))

    def dessiner_popup_defaite(self, ecran):
        """Dessine le popup de défaite"""
        self.maj_volume()
        
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)

        # Titre
        titre_surface = self.font.render("Game Over ! Vous êtes mort", True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 80
        ecran.blit(titre_surface, (titre_x, titre_y))

        # Ajuster les positions pour 2 boutons
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 160)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 250)

        # Liste des boutons avec leurs textes
        boutons = [
            (self.bouton_recommencer, "Recommencer"),
            (self.bouton_quitter, "Quitter")
        ]

        # Dessiner les boutons
        for rect, texte in boutons:
            # Effet de survol
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, (200, 200, 200), rect)
            else:
                pygame.draw.rect(ecran, (230, 230, 230), rect)

            # Bordure
            pygame.draw.rect(ecran, (0, 0, 0), rect, 3)

            # Texte du bouton
            texte_surface = self.font.render(texte, True, (0, 0, 0))
            texte_x = rect.x + (rect.width - texte_surface.get_width()) // 2
            texte_y = rect.y + (rect.height - texte_surface.get_height()) // 2
            ecran.blit(texte_surface, (texte_x, texte_y))
