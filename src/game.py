import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN
from grille import dessiner_grille
import joueur

# ----- INITIALISATION -----
pygame.init()
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption("ColorBlock")

horloge = pygame.time.Clock()

# ----- BOUCLE PRINCIPALE -----
while True:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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
    dessiner_grille(ecran)
    joueur.dessiner_joueur(ecran)
    pygame.display.flip()
    horloge.tick(60)
