import pygame
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN


def afficher_popup(message):
    ecran = pygame.display.get_surface()
    
    largeur_popup = 400
    hauteur_popup = 200
    popup_rect = pygame.Rect(
        (LARGEUR_ECRAN - largeur_popup) // 2,
        (HAUTEUR_ECRAN - hauteur_popup) // 2,
        largeur_popup,
        hauteur_popup
    )

    pygame.draw.rect(ecran, (255, 255, 255), popup_rect)
    pygame.draw.rect(ecran, (0, 0, 0), popup_rect, 2)

    font = pygame.font.Font(None, 36)
    texte = font.render(message, True, (0, 0, 0))
    texte_rect = texte.get_rect(center=popup_rect.center)
    ecran.blit(texte, texte_rect)

    pygame.display.flip()

    pygame.time.wait(2000)
