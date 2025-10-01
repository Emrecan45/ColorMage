import pygame
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Popup:
    """Affiche des messages à l'écran"""
    
    def afficher(ecran, message, duree=2000):
        """Affiche un popup avec un message
        
        Args:
            ecran: Surface pygame
            message: Texte à afficher
            duree: Durée d'affichage en millisecondes
        """
        largeur_popup = 400
        hauteur_popup = 200
        popup_rect = pygame.Rect((LARGEUR_ECRAN - largeur_popup) // 2, (HAUTEUR_ECRAN - hauteur_popup) // 2, largeur_popup, hauteur_popup)
        
        # Fond blanc avec bordure noire
        pygame.draw.rect(ecran, (255, 255, 255), popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), popup_rect, 2)
        
        # Texte centré
        font = pygame.font.Font(None, 36)
        texte = font.render(message, True, (0, 0, 0))
        texte_rect = texte.get_rect(center=popup_rect.center)
        ecran.blit(texte, texte_rect)
        
        pygame.display.flip()
        pygame.time.wait(duree)
