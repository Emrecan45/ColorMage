import pygame
import json
import os
import random
from config import TAILLE_CELLULE, COULEURS, GRAVITE, VITESSE_DEPLACEMENT, FORCE_SAUT, LARGEUR_GRILLE, HAUTEUR_GRILLE
from config_manager import ConfigManager


class Joueur:
    """Le mage qui change de couleur"""

    def __init__(self, x, y, gestionnaire_config=None):
        self.x_initial = x
        self.y_initial = y
        self.x = x
        self.y = y
        self.largeur = TAILLE_CELLULE
        self.hauteur = TAILLE_CELLULE
        self.couleur = "gris"
        
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
        
        # Chargement des touches
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.controls = self.gestionnaire_config.obtenir_controles()
        
        # Chargement des bruitages
        self.son_saut = pygame.mixer.Sound(os.path.join("audio", "jump.mp3"))
        self.son_mort = pygame.mixer.Sound(os.path.join("audio", "death.mp3"))
        self.son_victoire = pygame.mixer.Sound(os.path.join("audio", "win.mp3"))
        
        son_change_couleur1 = pygame.mixer.Sound(os.path.join("audio", "color_change1.mp3"))
        son_change_couleur2 = pygame.mixer.Sound(os.path.join("audio", "color_change2.mp3"))
        son_change_couleur3 = pygame.mixer.Sound(os.path.join("audio", "color_change3.mp3"))
        # Liste des sons de changements de couleur
        self.sons_changement = [son_change_couleur1, son_change_couleur2, son_change_couleur3]
        
        # Variable pour empêcher le spam des sons de changement de couleur
        self.dernier_changement_couleur = 0
        self.delai_changement_couleur = 200  # millisecondes entre chaque son
        
        # Appliquer les volumes initiaux
        self.maj_volume_effets()

        # Chargement des images
        self.images = dict()
        
        img_gris = pygame.image.load("img/joueur_gris.png")
        self.images["gris"] = pygame.transform.scale(img_gris, (self.largeur, self.hauteur))

        img_rouge = pygame.image.load("img/joueur_rouge.png")
        self.images["rouge"] = pygame.transform.scale(img_rouge, (self.largeur, self.hauteur))

        img_bleu = pygame.image.load("img/joueur_bleu.png")
        self.images["bleu"] = pygame.transform.scale(img_bleu, (self.largeur, self.hauteur))

        img_verte = pygame.image.load("img/joueur_vert.png")
        self.images["vert"] = pygame.transform.scale(img_verte, (self.largeur, self.hauteur))
    
    def reset(self):
        """Réinitialise le joueur à sa position de départ et sa couleur de base (gris)"""
        self.x = self.x_initial
        self.y = self.y_initial
        self.couleur = "gris"
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
    
    def deplacer(self, touches, niveau):
        """Gère le déplacement du joueur"""
        #Entrées clavier
        self.vitesse_x = 0
        if self.controls['gauche'] != "":
            if touches[pygame.key.key_code(self.controls['gauche'])]:
                self.vitesse_x = -VITESSE_DEPLACEMENT

        if self.controls['droite'] != "":
            if touches[pygame.key.key_code(self.controls['droite'])]:
                self.vitesse_x = VITESSE_DEPLACEMENT

        if self.controls['sauter'] != "":
            if touches[pygame.key.key_code(self.controls['sauter'])] and self.au_sol:
                self.vitesse_y = FORCE_SAUT
                self.au_sol = False
                self.son_saut.play()

        # Gravité
        self.vitesse_y += GRAVITE
        
        # Calcul nouvelles positions
        nouveau_x = self.x + self.vitesse_x
        nouveau_y = self.y + self.vitesse_y
        
        # Limites de l'ecran
        if nouveau_x < 0:
            nouveau_x = 0
            self.vitesse_x = 0
        if nouveau_x + self.largeur > LARGEUR_GRILLE * TAILLE_CELLULE:
            nouveau_x = LARGEUR_GRILLE * TAILLE_CELLULE - self.largeur
            self.vitesse_x = 0
        
        # Collision horizontale
        if self.vitesse_x != 0:
            rect = pygame.Rect(nouveau_x, self.y, self.largeur, self.hauteur)
            if niveau.collision(rect, self.couleur):
                while not niveau.collision(pygame.Rect(self.x + (1 if self.vitesse_x > 0 else -1), self.y, self.largeur, self.hauteur),self.couleur):
                    self.x += (1 if self.vitesse_x > 0 else -1)
                self.vitesse_x = 0
            else:
                self.x = nouveau_x
        
        # Collision verticale
        rect = pygame.Rect(self.x, nouveau_y, self.largeur, self.hauteur)
        if niveau.collision(rect, self.couleur):
            while not niveau.collision(pygame.Rect(self.x, self.y + (1 if self.vitesse_y > 0 else -1), self.largeur, self.hauteur),self.couleur):
                self.y += (1 if self.vitesse_y > 0 else -1)
            if self.vitesse_y > 0:
                self.au_sol = True
            self.vitesse_y = 0
        else:
            self.y = nouveau_y
            self.au_sol = False
    
    def interagir_avec_blocs(self, niveau):
        """Vérifie les interactions avec les blocs spéciaux"""
        bloc_x = int((self.x + self.largeur // 2) / TAILLE_CELLULE)
        bloc_y = int((self.y + self.hauteur // 2) / TAILLE_CELLULE)
        bloc = niveau.obtenir_bloc(bloc_x, bloc_y)
        
        if "change_" in bloc:
            # ca prend juste 'couleur' dans 'change_couleur'
            nouvelle_couleur = bloc.split("change_")[1]
            
            # vérifier si on change de couleur
            if self.couleur != nouvelle_couleur:
                # Vérifier le délai depuis le dernier son
                temps_actuel = pygame.time.get_ticks() # Renvoie le nombre de millisecondes depuis le lancement de pygame
                if temps_actuel - self.dernier_changement_couleur >= self.delai_changement_couleur:
                    self.couleur = nouvelle_couleur
                    # Arrêter tous les sons de changement en cours
                    for son in self.sons_changement:
                        son.stop()
                    # Jouer un nouveau son
                    son_change_aleatoire = random.choice(self.sons_changement)
                    son_change_aleatoire.play()
                    self.dernier_changement_couleur = temps_actuel
                else:
                    # Changer la couleur mais sans jouer de son
                    self.couleur = nouvelle_couleur
  
        if bloc == "porte":
            self.son_victoire.play()
            return "victoire"
        
        if bloc == "pic":
            self.son_mort.play()
            return "mort"
    
    def maj_controles(self):
        """Recharge les touches depuis le gestionnaire"""
        self.gestionnaire_config.charger_config()
        self.controls = self.gestionnaire_config.obtenir_controles()
        
    def maj_volume_effets(self):
        """Met à jour le volume de TOUS les effets sonores"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        volume = volumes.get("effets", 50) / 100
        
        # Mettre à jour tous les sons
        self.son_saut.set_volume(volume)
        self.son_mort.set_volume(volume)
        self.son_victoire.set_volume(volume)
        
        # Mettre à jour tous les sons de changement de couleur
        for son in self.sons_changement:
            son.set_volume(volume)
    
    def dessiner(self, ecran):
        """Dessine le joueur"""
        if self.couleur in self.images:
            ecran.blit(self.images[self.couleur], (self.x, self.y))
