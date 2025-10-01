import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, FPS, TAILLE_CELLULE
from joueur import Joueur
from niveau import Niveau
from popup import Popup
from pause import MenuPause


class Game:
    """Classe principale gérant le jeu"""

    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        pygame.display.set_caption("ColorMage")
        self.horloge = pygame.time.Clock()
        
        # Initialisation du niveau
        self.niveau = Niveau()
        self.niveau.charger_niveau_1()
        
        # Initialisation du joueur
        self.joueur = Joueur(0, HAUTEUR_ECRAN - 2*TAILLE_CELLULE)
        
        # Menu de pause
        self.menu_pause = MenuPause()
        
        self.en_cours = True
    
    def gerer_evenements(self):
        """Gère les événements pygame"""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False
            
            # Touche P pour mettre en pause
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_p:
                    self.menu_pause.afficher_menu(self.ecran, self.joueur, self.niveau)
            
            # Clic sur le bouton pause
            elif evenement.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_pause.bouton_rect.collidepoint(evenement.pos):
                    self.menu_pause.afficher_menu(self.ecran, self.joueur, self.niveau)
    
    def maj(self):
        """Met à jour la logique du jeu"""
        touches = pygame.key.get_pressed()
        self.joueur.deplacer(touches, self.niveau)
        
        # Vérifier interactions
        resultat = self.joueur.interagir_avec_blocs(self.niveau)
        
        if resultat == "victoire":
            Popup.afficher(self.ecran, "GG ! tu as gagné.")
            self.en_cours = False
        
        elif resultat == "mort":
            Popup.afficher(self.ecran, "Game Over ! tu es mort.")
            self.en_cours = False
    
    def afficher(self):
        """Dessine tous les éléments"""
        self.ecran.fill((255, 255, 255))
        self.niveau.dessiner(self.ecran)
        self.joueur.dessiner(self.ecran)
        self.menu_pause.dessiner_bouton(self.ecran)
        pygame.display.flip()
    
    def run(self):
        """Lance la boucle principale"""
        while self.en_cours:
            self.gerer_evenements()
            self.maj()
            self.afficher()
            self.horloge.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = Game()
    jeu.run()
