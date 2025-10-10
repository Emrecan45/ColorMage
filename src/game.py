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
        
        # Fond du jeu
        self.fond_jeu = pygame.image.load("img/fond_jeu.png")
        self.fond_jeu = pygame.transform.scale(self.fond_jeu, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        
        # Musique du jeu
        music_path = os.path.join("audio", "main_theme.mp3")
        pygame.mixer.music.load(music_path)
        # Appliquer le volume sauvegardé (de 0 à 100 converti en 0.0 à 1.0)
        volume_musique = volumes.get("musique", 50) / 100
        pygame.mixer.music.set_volume(volume_musique)
        pygame.mixer.music.play(-1)  # (-1) = musique qui tourne a l'infini
        
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN)) 
        pygame.display.set_caption("ColorMage")
        self.horloge = pygame.time.Clock()
        
        # État du jeu : "menu" ou "jeu" ou "parametres" ou "selection"
        self.etat = "menu"
        
        # Niveau
        self.niveau = Niveau()
        
        # Joueur
        self.joueur = Joueur(0, HAUTEUR_ECRAN - 2 * TAILLE_CELLULE, self.gestionnaire_config)
        
        # Menu d'accueil
        self.menu = Menu()
        
        # Pause
        self.pause = Pause()
        
        # Parametres
        self.parametres = Parametres(self.joueur, self.gestionnaire_config)
        
        self.menu_niveaux = MenuNiveaux()
        self.niveau_actuel = self.gestionnaire_config.obtenir_niveau_actuel()
        
        self.en_cours = True
        
        # Popups
        self.popup = Popup()
        self.popup_actif = None
    
    def gerer_evenements(self):
        """Gère les événements pygame"""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False

            if self.popup_actif is not None:
                if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                    # Gérer les clics selon le type de popup
                    if self.popup_actif == "victoire":
                        action = self.popup.gerer_clic_victoire(evenement.pos, self.niveau_actuel)
                    elif self.popup_actif == "defaite":
                        action = self.popup.gerer_clic_defaite(evenement.pos)
                    else:
                        action = None
                    
                    if action:
                        self.traiter_action_popup(action)
                        self.popup_actif = None
            else:
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
                        if resultat == 0:
                            self.etat = "menu"
                        elif resultat is not None and resultat > 0:
                            self.joueur.reset()
                            self.niveau_actuel = resultat
                            self.niveau.reset(resultat, self.ecran)
                            self.joueur.maj_controles()
                            self.niveau.charger_niveau(resultat, self.ecran)
                            self.joueur.reset()
                            self.joueur.maj_controles()
                            self.etat = "jeu"

                elif self.etat == "jeu":
                    if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_p:
                        self.pause.son_select.play()
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel)
                        if action == "quitter":
                            self.etat = "selection"
                    
                    # Gérer le clic sur le bouton pause
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        if self.pause.bouton_rect.collidepoint(evenement.pos):
                            self.pause.son_select.play()
                            action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel)
                            if action == "quitter":
                                self.etat = "selection"

    
    def traiter_action_popup(self, action):
        """Traite l'action sélectionnée dans un popup"""
        if action == "suivant":
            self.niveau_actuel += 1
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset()
            self.joueur.maj_controles()
            self.etat = "jeu"
        elif action == "rejouer":
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset()
            self.joueur.maj_controles()
            self.etat = "jeu"
        elif action == "quitter":
            self.etat = "selection"
    
    def maj(self):
        """Met à jour la logique du jeu"""
        # Ne pas mettre à jour si un popup est actif
        if self.popup_actif is not None:
            return None
            
        if self.etat == "jeu":
            touches = pygame.key.get_pressed()
            self.joueur.deplacer(touches, self.niveau)
            self.joueur.animer()
            # Stocke l'interaction du joueur
            resultat = self.joueur.interagir_avec_blocs(self.niveau)

            # Cas de victoire
            if resultat == "victoire":
                self.popup_actif = "victoire"
                # Débloquer le niveau suivant si c'etait pas deja le cas
                niveau_max = self.gestionnaire_config.obtenir_niveau_actuel()
                if self.niveau_actuel == niveau_max:
                    self.gestionnaire_config.maj_niveau_actuel(self.niveau_actuel + 1)

            # Cas de défaite
            elif resultat == "mort":
                self.popup_actif = "defaite"

    def afficher(self):
        """Dessine tous les éléments"""
        if self.etat == "menu":
            self.menu.afficher_menu(self.ecran)
            
        elif self.etat == "selection": 
            self.menu_niveaux.afficher_selection(self.ecran)
            
        elif self.etat == "jeu":
            self.ecran.blit(self.fond_jeu, (0, 0))
            self.niveau.dessiner(self.ecran)
            self.joueur.dessiner(self.ecran)
            self.pause.dessiner_bouton(self.ecran)
            
            # Afficher le popup s'il y en a un
            if self.popup_actif == "victoire":
                self.popup.dessiner_popup_victoire(self.ecran, self.niveau_actuel)
            elif self.popup_actif == "defaite":
                self.popup.dessiner_popup_defaite(self.ecran)

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
