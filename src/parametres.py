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
        action = "parametres"
        en_parametres = True
        bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20, 250, 50)
        
        while en_parametres:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_retour.collidepoint(event.pos):
                        action = "quitter"
                        en_parametres = False
                        
            ecran.blit(self.overlay, (0, 0))
            titre_txt = self.font.render("Parametres", True, (255, 255, 255))
            retour_txt = self.font.render("Retour", True, (255, 255, 255))
            pygame.draw.rect(ecran, (70, 70, 70), bouton_retour)
            ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 130))
            ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 25))
            pygame.display.flip()
            
        return action