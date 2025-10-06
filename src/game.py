import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, FPS, TAILLE_CELLULE
from joueur import Joueur
from niveau import Niveau
from popup import Popup
from pause import Pause
from menu import Menu
from parametres import Parametres

class Game:
    """Classe principale gérant le jeu"""

    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        pygame.display.set_caption("ColorMage")
        self.horloge = pygame.time.Clock()
        
        # État du jeu : "menu" ou "jeu" ou "parametres"
        self.etat = "menu"
        
        # Initialisation du niveau
        self.niveau = Niveau()
        self.niveau.charger_niveau_1()
        
        # Initialisation du joueur
        self.joueur = Joueur(0, HAUTEUR_ECRAN - 2*TAILLE_CELLULE)
        
        # Menu d'accueil
        self.menu = Menu()
        
        # Menu de pause
        self.pause = Pause()
        
        # Menu de parametres
        self.parametres = Parametres()
        
        self.en_cours = True
    
    def gerer_evenements(self):
        """Gère les événements pygame"""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False
            
            # Gestion des événements selon l'état
            if self.etat == "menu":
                if evenement.type == pygame.MOUSEBUTTONDOWN:
                    action = self.menu.gerer_clic(evenement.pos)
                    if action == "jouer":
                        self.etat = "jeu"
                        # Réinitialiser le jeu
                        self.joueur.reset()
                        self.niveau.reset()
                    elif action == "parametres":
                        self.etat = "param"
                    elif action == "quitter":
                        self.en_cours = False  
  
            elif self.etat == "param":
                if evenement.type == pygame.MOUSEBUTTONDOWN:
                    action = self.parametres.gerer_clic(evenement.pos)
                    if action == "quitter":
                        self.etat = "menu"
    
            elif self.etat == "jeu":
                # Touche P pour mettre en pause
                if evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_p:
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau)
                        if action == "quitter":
                            self.etat = "menu"
                
                # Clic sur le bouton pause
                if evenement.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause.bouton_rect.collidepoint(evenement.pos):
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau)
                        if action == "quitter":
                            self.etat = "menu"
    
    def maj(self):
        """Met à jour la logique du jeu"""
        if self.etat == "jeu":
            touches = pygame.key.get_pressed()
            self.joueur.deplacer(touches, self.niveau)
            
            # Vérifier interactions
            resultat = self.joueur.interagir_avec_blocs(self.niveau)
            
            if resultat == "victoire":
                Popup.afficher(self.ecran, "GG ! tu as gagné.")
                self.etat = "menu"
            
            elif resultat == "mort":
                Popup.afficher(self.ecran, "Game Over ! tu es mort.")
                self.etat = "menu"
    
    def afficher(self):
        """Dessine tous les éléments"""
        if self.etat == "menu":
            self.menu.afficher_menu(self.ecran)
        
        elif self.etat == "jeu":
            self.ecran.fill((255, 255, 255))
            self.niveau.dessiner(self.ecran)
            self.joueur.dessiner(self.ecran)
            self.pause.dessiner_bouton(self.ecran)

        elif self.etat == "param":
            self.parametres.afficher_parametres(self.ecran)
        
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
