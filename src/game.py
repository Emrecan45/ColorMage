import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN
import grille
import pause
import joueur

# ----- INITIALISATION -----
pygame.init()
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption("ColorBlock")

horloge = pygame.time.Clock()

# ----- BOUCLE PRINCIPALE -----
while True:
    bouton_rect = pause.dessiner_bouton(ecran)
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
             
        # Gestion du bouton et de la touche pause
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_p:
                pause.menu_pause(ecran)
        elif evenement.type == pygame.MOUSEBUTTONDOWN:
            if bouton_rect.collidepoint(evenement.pos):
                pause.menu_pause(ecran)

    touches = pygame.key.get_pressed()
    joueur.vitesse_x = 0
    if touches[pygame.K_LEFT]:
        joueur.vitesse_x = -joueur.vitesse
    if touches[pygame.K_RIGHT]:
        joueur.vitesse_x = joueur.vitesse
    if touches[pygame.K_UP] and joueur.au_sol:
        joueur.vitesse_y = joueur.force_saut
        joueur.au_sol = False

    joueur.deplacer_joueur()

    ecran.fill((255, 255, 255))
    grille.dessiner_grille(ecran)
    joueur.dessiner_joueur(ecran)
    pause.dessiner_bouton(ecran)
    pygame.display.flip()
    horloge.tick(60)
