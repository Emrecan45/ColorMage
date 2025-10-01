import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN
import joueur as j
import grille as g

def dessiner_bouton(ecran):
    largeur_bouton = 70
    hauteur_bouton = 70
    marge = 15

    image_pause = pygame.image.load("../img/pause.png")
    image_pause = pygame.transform.scale(image_pause, (largeur_bouton, hauteur_bouton))
    ecran.blit(image_pause, (LARGEUR_ECRAN - largeur_bouton - marge, marge))

    bouton_rect = pygame.Rect(LARGEUR_ECRAN - largeur_bouton - marge, marge, largeur_bouton, hauteur_bouton)
    return bouton_rect


    
def menu_pause(ecran):
    font = pygame.font.SysFont(None, 50)

    bouton_continuer = pygame.Rect(LARGEUR_ECRAN//2 -125, HAUTEUR_ECRAN//2 -140 , 250, 50)
    bouton_recommencer = pygame.Rect(LARGEUR_ECRAN//2 -125, HAUTEUR_ECRAN//2 -60, 250, 50)
    bouton_quitter = pygame.Rect(LARGEUR_ECRAN//2 -125, HAUTEUR_ECRAN//2 + 20, 250, 50)

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_continuer.collidepoint(event.pos):
                    paused = False
                if bouton_recommencer.collidepoint(event.pos):
                    paused = False
                    j.reset()
                    g.reset()
                if bouton_quitter.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    paused = False  # Appuyer sur Échap ou P quitte le menu pause

        # Fond semi-transparent
        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        ecran.blit(overlay, (0, 0))

        # Boutons
        pygame.draw.rect(ecran, (70, 70, 70), bouton_continuer)
        pygame.draw.rect(ecran, (70, 70, 70), bouton_recommencer)
        pygame.draw.rect(ecran, (70, 70, 70), bouton_quitter)

        # Texte boutons
        contiuner_txt = font.render("Continuer", True, (255, 255, 255))
        recommencer_txt = font.render("Recommencer", True, (255, 255, 255))
        quitter_txt = font.render("Quitter", True, (255, 255, 255))

        ecran.blit(contiuner_txt, (LARGEUR_ECRAN//2 - contiuner_txt.get_width()//2, HAUTEUR_ECRAN//2 -130))
        ecran.blit(recommencer_txt, (LARGEUR_ECRAN//2 - recommencer_txt.get_width()//2, HAUTEUR_ECRAN//2 - 50))
        ecran.blit(quitter_txt, (LARGEUR_ECRAN//2 - quitter_txt.get_width()//2, HAUTEUR_ECRAN//2 + 30))

        pygame.display.flip()
