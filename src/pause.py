import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Pause:
    """Gère le menu de pause avec bouton et options"""
    
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
    
    def dessiner_bouton(self, ecran):
        """Dessine le bouton de pause en haut à droite"""
        ecran.blit(self.image_pause, (self.bouton_x, self.bouton_y))
    
    def afficher_pause(self, ecran, joueur, niveau):
        """Affiche le menu de pause avec options
        
        Returns:
            str: "continuer", "recommencer", ou "quitter"
        """
        font = pygame.font.SysFont(None, 50)
        
        # Boutons du menu
        bouton_continuer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 140, 250, 50)
        bouton_recommencer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 60, 250, 50)
        bouton_quitter = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20, 250, 50)
        
        en_pause = True
        action = "continuer"
        
        while en_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_continuer.collidepoint(event.pos):
                        action = "continuer"
                        en_pause = False
                    elif bouton_recommencer.collidepoint(event.pos):
                        action = "recommencer"
                        en_pause = False
                    elif bouton_quitter.collidepoint(event.pos):
                        action = "quitter"
                        en_pause = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        action = "continuer"
                        en_pause = False
            
            # Fond noir
            overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
            overlay.fill((0, 0, 0))
            ecran.blit(overlay, (0, 0))
            
            # Dessiner les boutons
            pygame.draw.rect(ecran, (70, 70, 70), bouton_continuer)
            pygame.draw.rect(ecran, (70, 70, 70), bouton_recommencer)
            pygame.draw.rect(ecran, (70, 70, 70), bouton_quitter)
            
            # Textes des boutons
            continuer_txt = font.render("Continuer", True, (255, 255, 255))
            recommencer_txt = font.render("Recommencer", True, (255, 255, 255))
            quitter_txt = font.render("Quitter", True, (255, 255, 255))
            
            ecran.blit(continuer_txt, (LARGEUR_ECRAN // 2 - continuer_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
            ecran.blit(recommencer_txt, (LARGEUR_ECRAN // 2 - recommencer_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 50))
            ecran.blit(quitter_txt, (LARGEUR_ECRAN // 2 - quitter_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 30))
            
            pygame.display.flip()
        
        # Exécuter l'action demandée
        if action == "recommencer":
            joueur.reset()
            niveau.reset()
        return action