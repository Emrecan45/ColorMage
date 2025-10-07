import pygame
import sys
import os
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, FPS, TAILLE_CELLULE
from joueur import Joueur
from niveau import Niveau
from popup import Popup
from pause import Pause
from menu import Menu
from parametres import Parametres
from config_manager import ConfigManager
from menu_niveaux import MenuNiveaux

class Game:
    """Classe principale gérant le jeu"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Charger la configuration
        self.gestionnaire_config = ConfigManager()
        volumes = self.gestionnaire_config.obtenir_volumes()
        
        # Musique du jeu
        music_path = os.path.join("audio", "main_theme.mp3")
        pygame.mixer.music.load(music_path)
        # Appliquer le volume sauvegardé (de 0 à 100 converti en 0.0 à 1.0)
        volume_musique = volumes.get("musique", 50) / 100
        pygame.mixer.music.set_volume(volume_musique)
        pygame.mixer.music.play(-1)  # (-1) = boucle infinie
        
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN)) 
        pygame.display.set_caption("ColorMage")
        self.horloge = pygame.time.Clock()
        
        # État du jeu : "menu" ou "jeu" ou "parametres"
        self.etat = "menu"
        
        # Initialisation du niveau
        self.niveau = Niveau()
        
        # Initialisation du joueur
        self.joueur = Joueur(0, HAUTEUR_ECRAN - 2*TAILLE_CELLULE)
        
        # Menu d'accueil
        self.menu = Menu()
        
        # Menu de pause
        self.pause = Pause()
        
        # Menu de parametres
        self.parametres = Parametres(self.joueur)
        
        self.menu_niveaux = MenuNiveaux()
        self.niveau_actuel = self.gestionnaire_config.obtenir_niveau_actuel()
        
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
                        self.etat = "selection"
                    elif action == "parametres":
                        self.etat = "param"
                    elif action == "quitter":
                        self.en_cours = False
  
            elif self.etat == "param":
                action = self.parametres.gerer_events(evenement)
                if action == "quitter":
                    self.etat = "menu"

            elif self.etat == "selection":
                if evenement.type == pygame.MOUSEBUTTONDOWN:
                    resultat = self.menu_niveaux.gerer_clic(evenement.pos)
                    if resultat == 0:  # Bouton retour
                        self.etat = "menu"
                    elif resultat is not None and resultat > 0:  # Un niveau a été choisi
                        if resultat == 1: 
                            # Réinitialiser le jeu
                            self.joueur.reset()
                            self.niveau.reset(resultat, self.ecran)
                            self.joueur.maj_controles()
                            self.niveau_actuel = resultat
                            self.niveau.charger_niveau(resultat, self.ecran)
                            self.joueur.reset()
                            self.joueur.maj_controles()
                            self.etat = "jeu"
                        else:
                            Popup.afficher(self.ecran, "Niveau non disponible", duree=1000)
                                    
            elif self.etat == "jeu":
                # Touche P pour mettre en pause
                if evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_p:
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau)
                        if action == "quitter":
                            self.etat = "selection"
                
                # Clic sur le bouton pause
                if evenement.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause.bouton_rect.collidepoint(evenement.pos):
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau)
                        if action == "quitter":
                            self.etat = "selection"
    
    def maj(self):
        """Met à jour la logique du jeu"""
        if self.etat == "jeu":
            touches = pygame.key.get_pressed()
            self.joueur.deplacer(touches, self.niveau)
            
            # Vérifier interactions
            resultat = self.joueur.interagir_avec_blocs(self.niveau)
            
            if resultat == "victoire":
                Popup.afficher(self.ecran, "Bravo ! vous avez gagné.")
                self.gestionnaire_config.maj_niveau_actuel(self.niveau_actuel + 1)
                self.etat = "selection"
            
            elif resultat == "mort":
                Popup.afficher(self.ecran, "Game Over ! vous êtes mort.")
                self.etat = "selection"
    
    def afficher(self):
        """Dessine tous les éléments"""
        if self.etat == "menu":
            self.menu.afficher_menu(self.ecran)
            
        elif self.etat == "selection": 
            self.menu_niveaux.afficher_selection(self.ecran)
            
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
