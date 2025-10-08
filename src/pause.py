import pygame
import sys
import os
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN
from config_manager import ConfigManager

class Pause:
    """Gère le menu de pause avec bouton et options"""
    
    def __init__(self):
        self.largeur_bouton = 70
        self.hauteur_bouton = 70
        self.marge = 15
        self.image_pause = pygame.image.load("img/pause.png")
        self.image_pause = pygame.transform.scale(self.image_pause, (self.largeur_bouton, self.hauteur_bouton))
        
        # son des clics
        self.gestionnaire_config = ConfigManager()
        self.son_select = pygame.mixer.Sound(os.path.join("audio", "select.mp3"))
        
        # Coordonnées du bouton pause
        self.bouton_x = LARGEUR_ECRAN - self.largeur_bouton - self.marge
        self.bouton_y = self.marge
        self.bouton_rect = pygame.Rect(self.bouton_x, self.bouton_y, self.largeur_bouton, self.hauteur_bouton)
        
        # Police
        self.font = pygame.font.Font(None, 48)
        
        # Dimensions du popup
        self.largeur_popup = 600
        self.hauteur_popup = 400
        self.popup_rect = pygame.Rect(
            (LARGEUR_ECRAN - self.largeur_popup) // 2, 
            (HAUTEUR_ECRAN - self.hauteur_popup) // 2, 
            self.largeur_popup, 
            self.hauteur_popup
        )
        
        # Créer les boutons du menu pause
        self.bouton_continuer = pygame.Rect(0, 0, 260, 60)
        self.bouton_continuer.center = (self.popup_rect.centerx, self.popup_rect.top + 160)
        
        self.bouton_recommencer = pygame.Rect(0, 0, 260, 60)
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 250)
        
        self.bouton_quitter = pygame.Rect(0, 0, 260, 60)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 340)
    
    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
    
    def dessiner_bouton(self, ecran):
        """Dessine le bouton de pause en haut à droite"""
        ecran.blit(self.image_pause, (self.bouton_x, self.bouton_y))
    
    def dessiner_popup(self, ecran):
        """Dessine le popup de pause avec tous les boutons"""
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)
        
        # Titre
        titre_surface = self.font.render("Pause", True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 80
        ecran.blit(titre_surface, (titre_x, titre_y))
        
        # Liste des boutons avec leurs textes
        boutons = [
            (self.bouton_continuer, "Continuer"),
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
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu pause
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "continuer", "recommencer", "quitter" ou None
        """
        if self.bouton_continuer.collidepoint(pos):
            return "continuer"
        elif self.bouton_recommencer.collidepoint(pos):
            return "recommencer"
        elif self.bouton_quitter.collidepoint(pos):
            return "quitter"
        return None
    
    def afficher_pause(self, ecran, joueur, niveau, numero_niveau):
        """Affiche le menu de pause avec options
        
        Args:
            ecran: Surface pygame pour l'affichage
            joueur: Instance du joueur
            niveau: Instance du niveau
            numero_niveau: Numéro du niveau actuel
        
        Returns:
            str: "continuer", "recommencer", ou "quitter"
        """
        en_pause = True
        action = "continuer"
        self.maj_volume()
        
        while en_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = self.gerer_clic(event.pos)
                    self.son_select.play()
                    if action:
                        en_pause = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.son_select.play()
                        action = "continuer"
                        en_pause = False
            
            # Redessiner le niveau et le joueur en arrière-plan
            fond_jeu = pygame.image.load("img/fond_jeu.png")
            fond_jeu = pygame.transform.scale(fond_jeu, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
            ecran.blit(fond_jeu, (0, 0))
            niveau.dessiner(ecran)
            joueur.dessiner(ecran)
            self.dessiner_bouton(ecran)
            
            # Dessiner le popup de pause
            self.dessiner_popup(ecran)
            
            pygame.display.flip()
        
        # Exécuter l'action demandée
        if action == "recommencer":
            joueur.reset()
            niveau.reset(numero_niveau, ecran)
        return action
