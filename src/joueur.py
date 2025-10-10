import pygame
import json
import os
import random
import math
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
        self.etait_au_sol = True
        
        # Direction du personnage (1 = droite, -1 = gauche)
        self.direction = 1
        
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
        
        # variable pour empêcher le spam des sons de changement de couleur
        self.dernier_changement_couleur = 0
        self.delai_changement_couleur = 200  # millisecondes entre chaque son
        
        # Appliquer les parametres de volumes
        self.maj_volume_effets()

        # Chargement des spritesheets
        self.spritesheets = dict()
        self.images = dict()
        couleurs = ["gris", "rouge", "bleu", "vert"]
        
        # Dimensions d'un sprite dans le spritesheet (768x590 divisé par 4 colonnes x 3 lignes)
        self.sprite_largeur = 192  # 768 ÷ 4
        self.sprite_hauteur = 196  # 590 ÷ 3
        
        for couleur in couleurs:
            # Charger le spritesheet
            chemin = "img/joueur_" + couleur + ".png"
            spritesheet = pygame.image.load(chemin)
            self.spritesheets[couleur] = spritesheet
            
            # Extraire les frames du spritesheet
            frames = []
            
            positions = [
                #repos
                (0, 0),
                
                # saut
                (2, 2),  # debut du saut
                (3, 2)   # milieu du saut
            ]
            
            for col, ligne in positions:
                x_sprite = col * self.sprite_largeur
                y_sprite = ligne * self.sprite_hauteur
                
                #extraire le sprite
                sprite = spritesheet.subsurface(
                    pygame.Rect(x_sprite, y_sprite, self.sprite_largeur, self.sprite_hauteur)
                )
                
                sprite = pygame.transform.scale(sprite, (self.largeur, self.hauteur))
                frames.append(sprite)
            
            self.images[couleur] = frames

        self.frame_index = 0
        self.temps_derniere_frame = 0
        self.delai_animation = 50
        self.en_animation = False
        self.type_animation = None
        self.animation_terminee = False
    
    def reset(self):
        """Réinitialise le joueur à sa position de départ et sa couleur de base (gris)"""
        self.x = self.x_initial
        self.y = self.y_initial
        self.couleur = "gris"
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
        self.etait_au_sol = True
        self.direction = 1
        self.en_animation = False
        self.type_animation = None
        self.animation_terminee = False
        self.frame_index = 0
    
    def deplacer(self, touches, niveau):
        """Gère le déplacement du joueur"""
        self.etait_au_sol = self.au_sol
        
        # Entrées clavier
        self.vitesse_x = 0
        if self.controls['gauche'] != "":
            if touches[pygame.key.key_code(self.controls['gauche'])]:
                self.vitesse_x = -VITESSE_DEPLACEMENT
                self.direction = -1  # Tourner vers la gauche

        if self.controls['droite'] != "":
            if touches[pygame.key.key_code(self.controls['droite'])]:
                self.vitesse_x = VITESSE_DEPLACEMENT
                self.direction = 1  # Tourner vers la droite

        if self.controls['sauter'] != "":
            if touches[pygame.key.key_code(self.controls['sauter'])] and self.au_sol:
                self.vitesse_y = FORCE_SAUT
                self.au_sol = False
                self.son_saut.play()
                self.demarrer_animation("saut")

        # Gravite
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
                while not niveau.collision(pygame.Rect(self.x + (1 if self.vitesse_x > 0 else -1), self.y, self.largeur, self.hauteur), self.couleur):
                    self.x += (1 if self.vitesse_x > 0 else -1)
                self.vitesse_x = 0
            else:
                self.x = nouveau_x
        
        # Collision verticale
        rect = pygame.Rect(self.x, nouveau_y, self.largeur, self.hauteur)
        if niveau.collision(rect, self.couleur):
            while not niveau.collision(pygame.Rect(self.x, self.y + (1 if self.vitesse_y > 0 else -1), self.largeur, self.hauteur), self.couleur):
                self.y += (1 if self.vitesse_y > 0 else -1)
            if self.vitesse_y > 0:
                self.au_sol = True
                # renitialiser l'animation quand on touche le sol
                if self.en_animation:
                    self.en_animation = False
                    self.type_animation = None
                    self.animation_terminee = False
                    self.frame_index = 0
            self.vitesse_y = 0
        else:
            self.y = nouveau_y
            self.au_sol = False
        
        # chute
        if self.etait_au_sol and not self.au_sol and self.type_animation != "saut":
            self.demarrer_animation("chute")
    
    def demarrer_animation(self, type_anim):
        """Démarre une nouvelle animation si aucune n'est en cours"""
        if not self.en_animation or (self.en_animation and self.type_animation == "chute" and type_anim == "saut"):
            self.en_animation = True
            self.type_animation = type_anim
            self.frame_index = 1  # commence a la première frame (pas la frame "repos")
            self.temps_derniere_frame = pygame.time.get_ticks()
            self.animation_terminee = False
    
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
                temps_actuel = pygame.time.get_ticks()
                if temps_actuel - self.dernier_changement_couleur >= self.delai_changement_couleur:
                    self.couleur = nouvelle_couleur
                    for son in self.sons_changement:
                        son.stop()
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
    
    def animer(self):
        """Joue l'animation de saut/chute une seule fois"""
        if self.en_animation and not self.animation_terminee:
            temps_actuel = pygame.time.get_ticks()
            if temps_actuel - self.temps_derniere_frame >= self.delai_animation:
                self.temps_derniere_frame = temps_actuel
                if self.frame_index < len(self.images[self.couleur]) - 1:
                    self.frame_index += 1
                else:
                    # Fin de l'animation de saut
                    self.animation_terminee = True
        
        if not self.au_sol and self.animation_terminee:
            self.frame_index = len(self.images[self.couleur]) - 1
        
        # Quand le joueur touche le sol, on remet à l'état initial
        if self.au_sol and not self.en_animation:
            self.frame_index = 0
    
    def dessiner(self, ecran):
        """Dessine le joueur avec effet miroir en fonction du sens"""
        frames = self.images[self.couleur]
        image_res = frames[self.frame_index]
        if self.direction == -1:
            image = pygame.transform.flip(image_res, True, False)
        else:
            image = image_res
        ecran.blit(image, (self.x, self.y))
