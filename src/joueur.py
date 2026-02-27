import pygame
import json
import os
import random
import math
from config import TAILLE_CELLULE, COULEURS, GRAVITE, VITESSE_DEPLACEMENT, FORCE_SAUT, LARGEUR_GRILLE, HAUTEUR_GRILLE
from config_manager import ConfigManager


class Joueur:
    """Le mage qui change de couleur"""

    def __init__(self, x=None, y=None, gestionnaire_config=None):
        if x is None or y is None:
            self.x_initial = 0
            self.y_initial = 0
            self.x = 0
            self.y = 0
        else:
            self.x_initial = x
            self.y_initial = y - TAILLE_CELLULE
            self.x = x
            self.y = y
        self.visual_x = self.x
        self.visual_y = self.y
        self.largeur = TAILLE_CELLULE * 2
        self.hauteur = TAILLE_CELLULE * 2
        self.couleur = "gris"
        
        #hitbox
        self.marge_x = 40
        self.marge_y_haut = 10
        self.marge_y_bas = 2
        
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
        self.son_saut = pygame.mixer.Sound(os.path.join("audio", "jump.wav"))
        self.son_mort = pygame.mixer.Sound(os.path.join("audio", "death.wav"))
        self.son_victoire = pygame.mixer.Sound(os.path.join("audio", "win.wav"))
        
        son_change_couleur1 = pygame.mixer.Sound(os.path.join("audio", "color_change1.wav"))
        son_change_couleur2 = pygame.mixer.Sound(os.path.join("audio", "color_change2.wav"))
        son_change_couleur3 = pygame.mixer.Sound(os.path.join("audio", "color_change3.wav"))
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
        self.images_boules = dict()
        couleurs = ["gris", "rouge", "bleu", "vert"]
        
        # Dimensions d'un sprite dans le spritesheet (768x590 divisé par 4 colonnes x 3 lignes)
        self.sprite_largeur = 192  # 768 / 4
        self.sprite_hauteur = 196  # 590 / 3
        
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
                (2, 1),  # debut du saut
                (3, 1),  # milieu du saut
                (1, 2)   # fin du saut
            ]
            
            for col, ligne in positions:
                x_sprite = col * self.sprite_largeur
                y_sprite = ligne * self.sprite_hauteur
                
                #extraire le sprite
                sprite = spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_largeur, self.sprite_hauteur))
                sprite = pygame.transform.scale(sprite, (self.largeur, self.hauteur))
                frames.append(sprite)
            
            self.images[couleur] = frames
            
            positions_boules = {
                "rouge": (1, 1),
                "bleu":  (2, 0),
                "vert":  (0, 1)
            }

            boules = {}
            for couleur_boule, (col, ligne) in positions_boules.items():
                x_sprite = col*self.sprite_largeur
                y_sprite = ligne*self.sprite_hauteur

                sprite = spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_largeur, self.sprite_hauteur))
                sprite = pygame.transform.scale(sprite, (self.largeur, self.hauteur))
                boules[couleur_boule] = sprite

            boules["gris"] = self.images[couleur][0]
            self.images_boules[couleur] = boules

        self.frame_index = 0
        self.temps_derniere_frame = 0
        self.temps_changement_couleur = 0
        self.delai_animation = 50
        self.en_animation = False
        self.type_animation = None
        self.animation_terminee = False
        self.en_changement_couleur = False
        self.etape_changement = 0
        self.couleur_cible = None
        self.couleur_precedente = None

        # Caches pour les images retournées et les masques de collision
        self.cache_retournes = {}
        self.cache_masques = {}
        self.combo_cache = {}
    
    def reset(self, niveau=None):
        """Réinitialise le joueur à sa position de départ et sa couleur de base (gris)"""
        if niveau is not None:
            spawn_px = niveau.obtenir_spawn_pixel()
            if spawn_px is not None:
                self.x_initial, self.y_initial = spawn_px

        self.x = self.x_initial
        self.y = self.y_initial
        self.visual_x = self.x
        self.visual_y = self.y
        self.couleur = "gris"
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.direction = 1
        self.en_animation = False
        self.type_animation = None
        self.animation_terminee = False
        self.frame_index = 0
        self.en_changement_couleur = False
        self.etape_changement = 0
        self.couleur_cible = None
        self.couleur_precedente = None
        self.au_sol = False
        self.etait_au_sol = False
        if niveau is not None:
            rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut,
                               self.largeur - 2 * self.marge_x,
                               self.hauteur - self.marge_y_haut - self.marge_y_bas)
            if niveau.collision(rect, self.couleur):
                self.au_sol = True
                self.etait_au_sol = True
            else:
                # Pas au sol : démarrer immédiatement l'animation de chute
                self.au_sol = False
                self.etait_au_sol = False
                self.demarrer_animation("chute")
    
    def deplacer(self, touches, niveau):
        """Gère le déplacement du joueur"""
        self.etait_au_sol = self.au_sol
        self.pousse_plateforme = False
        if self.en_changement_couleur and self.etape_changement < 3:
            facteur_ralenti = 0.25 # ralenti pendant changement de couleur
        else:
            facteur_ralenti = 1.0

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

        # Gravite (ralentie pendant le changement de couleur)
        self.vitesse_y += GRAVITE * facteur_ralenti
        
        # Calcul nouvelles positions
        nouveau_x = self.x + self.vitesse_x * facteur_ralenti
        nouveau_y = self.y + self.vitesse_y * facteur_ralenti
        
        # Limites de l'ecran
        hitbox_gauche = nouveau_x + self.marge_x
        hitbox_droite = nouveau_x + self.largeur - self.marge_x
        
        if hitbox_gauche < 0:
            nouveau_x = -self.marge_x
            self.vitesse_x = 0
        if hitbox_droite > LARGEUR_GRILLE * TAILLE_CELLULE:
            nouveau_x = LARGEUR_GRILLE * TAILLE_CELLULE - self.largeur + self.marge_x
            self.vitesse_x = 0
        
        # Collision horizontale
        if self.vitesse_x != 0:
            self.x = nouveau_x
            rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
            if niveau.collision(rect, self.couleur):
                self.x = nouveau_x - self.vitesse_x
                rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
                while not niveau.collision(rect, self.couleur):
                    self.x += (1 if self.vitesse_x > 0 else -1)
                    rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
                self.x -= (1 if self.vitesse_x > 0 else -1)
                self.vitesse_x = 0
        
        # Collision verticale
        self.y = nouveau_y
        rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
        if niveau.collision(rect, self.couleur):
            self.y = nouveau_y - self.vitesse_y
            rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, 
                              self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
            while not niveau.collision(rect, self.couleur):
                self.y += (1 if self.vitesse_y > 0 else -1)
                rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, 
                                  self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
            self.y -= (1 if self.vitesse_y > 0 else -1)
            
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
            self.au_sol = False

        # tomber dans le vide
        if self.y > (HAUTEUR_GRILLE * TAILLE_CELLULE):
            return "mort"
        
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
    
    def demarrer_changement_couleur(self, nouvelle_couleur):
        """Démarre l'animation de changement de couleur"""
        if nouvelle_couleur != self.couleur:
            self.en_changement_couleur = True
            self.etape_changement = 0
            self.couleur_precedente = self.couleur
            self.couleur_cible = nouvelle_couleur
            self.temps_changement_couleur = pygame.time.get_ticks()
            
            # Arrêter tous les sons de changement en cours et jouer un nouveau
            for son in self.sons_changement:
                son.stop()
            son_change_aleatoire = random.choice(self.sons_changement)
            son_change_aleatoire.play()
    
    def animer_changement_couleur(self):
        """Gère l'animation de changement de couleur par étapes"""
        if not self.en_changement_couleur:
            return
        
        temps_actuel = pygame.time.get_ticks()
        
        if self.etape_changement == 0:
            delai_etape = 350#ms
        else:
            delai_etape = 100#ms
        
        if temps_actuel - self.temps_changement_couleur >= delai_etape:
            self.temps_changement_couleur = temps_actuel
            self.etape_changement += 1
            
            if self.etape_changement >= 4:
                # Fin de l'animation
                self.en_changement_couleur = False
                self.etape_changement = 0
                self.couleur_precedente = None
    
    def interagir_avec_blocs(self, niveau):
        """Vérifie les interactions avec les blocs spéciaux"""
        hitbox = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut, self.largeur - 2 * self.marge_x, self.hauteur - self.marge_y_haut - self.marge_y_bas)
        
        # Vérifier tous les blocs que la hitbox touche
        x_debut = int(hitbox.left / TAILLE_CELLULE)
        x_fin = int(hitbox.right / TAILLE_CELLULE)
        y_debut = int(hitbox.top / TAILLE_CELLULE)
        y_fin = int(hitbox.bottom / TAILLE_CELLULE)
        
        # Pour chaque blocs touchés par la hitbox
        for y in range(y_debut, y_fin + 1):
            for x in range(x_debut, x_fin + 1):
                bloc = niveau.obtenir_bloc(x, y)
                bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                player_mask = self.obtenir_masque_courant()
                bloc_mask = None

                # potions
                if "change_" in bloc and hasattr(niveau, 'masks_potion') and niveau.masks_potion.get(bloc) is not None:
                    bloc_mask = niveau.masks_potion.get(bloc)
                    base_lift, bob = niveau.obtenir_decalage_potion(x, y)
                    offset = (int(bloc_rect.left - self.x), int(bloc_rect.top - self.y - bob - base_lift))
                
                # pics
                elif bloc == "pic" and getattr(niveau, 'image_pic', None) is not None:
                    bloc_mask = pygame.mask.from_surface(niveau.image_pic)
                    offset = (int(bloc_rect.left - self.x), int(bloc_rect.top - self.y))
                
                # autres
                else:
                    bloc_mask = pygame.mask.Mask((TAILLE_CELLULE, TAILLE_CELLULE), fill=True)
                    offset = (int(bloc_rect.left - self.x), int(bloc_rect.top - self.y))

                touche = False
                if player_mask is not None and bloc_mask is not None:
                    if player_mask.overlap(bloc_mask, offset) is not None:
                        touche = True
                else:
                    if hitbox.colliderect(bloc_rect):
                        touche = True

                if "change_" in bloc:
                    if touche:
                        # ça prend juste 'couleur' dans 'change_couleur'
                        nouvelle_couleur = bloc.split("change_")[1]
                        
                        # vérifier si on change de couleur
                        if self.couleur != nouvelle_couleur and not self.en_changement_couleur:
                            self.demarrer_changement_couleur(nouvelle_couleur)
                            return None
        
                if bloc == "porte":
                    if touche:
                        return "teleportation"
                
                if bloc == "pic":
                    if touche:
                        return "mort"
        
        return None
    
    def maj_controles(self):
        """Recharge les touches depuis le gestionnaire"""
        self.gestionnaire_config.charger_config()
        self.controls = self.gestionnaire_config.obtenir_controles()
        
    def maj_volume_effets(self):
        """Met à jour le volume des effets sonores"""
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
        if self.en_changement_couleur:
            self.animer_changement_couleur()
            return None
        
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
        image_res = None
        
        if self.en_changement_couleur:
            if self.etape_changement == 0:
                # Affiche la boule de couleur cible (effet visuel)
                image_res = self.obtenir_image_boule_changement()
            else:
                self.couleur = self.couleur_cible
                image_res = self.images[self.couleur][0]

        else:
            frames = self.images[self.couleur]
            image_res = frames[self.frame_index]

        if self.direction == -1:
            if self.en_changement_couleur and self.etape_changement == 0:
                key = (self.couleur_precedente, self.couleur_cible)
                keyf = (self.couleur_precedente, self.couleur_cible, 'flip')
                img = self.combo_cache.get(keyf)
                if img is None:
                    base = self.combo_cache.get(key)
                    if base is None:
                        base = image_res
                        self.combo_cache[key] = base
                    img = pygame.transform.flip(base, True, False)
                    self.combo_cache[keyf] = img
            else:
                cle = (self.couleur, self.frame_index)
                img = self.cache_retournes.get(cle)
                if img is None:
                    img = pygame.transform.flip(image_res, True, False)
                    self.cache_retournes[cle] = img
        else:
            img = image_res

        self.visual_x = self.x
        self.visual_y = self.y
        ecran.blit(img, (self.x, self.y))

    def obtenir_image_courante(self):
        """Retourne la surface courante du joueur (flip appliqué si nécessaire)."""
        if self.en_changement_couleur:
            if self.etape_changement == 0:
                key = (self.couleur_precedente, self.couleur_cible)
                keyf = (self.couleur_precedente, self.couleur_cible, 'flip')
                if self.direction == -1:
                    img = self.combo_cache.get(keyf)
                    if img is None:
                        base = self.combo_cache.get(key)
                        if base is None:
                            base = self.obtenir_image_boule_changement()
                            self.combo_cache[key] = base
                        img = pygame.transform.flip(base, True, False)
                        self.combo_cache[keyf] = img
                    return img
                else:
                    img = self.combo_cache.get(key)
                    if img is None:
                        img = self.obtenir_image_boule_changement()
                        self.combo_cache[key] = img
                    return img
            return self.images[self.couleur][0]
        image_res = self.images[self.couleur][self.frame_index]
        if self.direction == -1:
            cle = (self.couleur, self.frame_index)
            img = self.cache_retournes.get(cle)
            if img is None:
                img = pygame.transform.flip(image_res, True, False)
                self.cache_retournes[cle] = img
            return img
        return image_res

    def obtenir_masque_courant(self):
        """Retourne le masque pré calculé correspondant à l'image courante."""
        # Pour l'animation de changement de couleur, on calcule sans cache
        if self.en_changement_couleur:
            img = self.obtenir_image_courante()
            return pygame.mask.from_surface(img)
        cle = (self.couleur, self.frame_index, self.direction)
        masque = self.cache_masques.get(cle)
        if masque is None:
            img = self.obtenir_image_courante()
            masque = pygame.mask.from_surface(img)
            self.cache_masques[cle] = masque
        return masque

    def obtenir_image_boule_changement(self):
        """Retourne l'image tenue_précédente + orb_cible (avec cache)."""
        prev = self.couleur_precedente
        target = self.couleur_cible
        key = (prev, target)

        # retour depuis le cache si déjà constitué
        combo = self.combo_cache.get(key)
        if combo:
            return combo

        if prev and prev in self.images_boules and target in self.images_boules[prev]:
            combo = self.images_boules[prev][target]
        elif target in self.images_boules and target in self.images_boules[target]:
            combo = self.images_boules[target][target]
        else:
            base = None
            orb = None
            if prev in self.images and len(self.images[prev]) > 0:
                base = self.images[prev][0]
            elif target in self.images and len(self.images[target]) > 0:
                base = self.images[target][0]

            if prev in self.images_boules and target in self.images_boules.get(prev, {}):
                orb = self.images_boules[prev][target]
            elif target in self.images_boules and target in self.images_boules.get(target, {}):
                orb = self.images_boules[target][target]
            elif target in self.images and len(self.images[target]) > 0:
                orb = self.images[target][0]

            surf = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            if base:
                surf.blit(base, (0, 0))
            if orb:
                surf.blit(orb, (0, 0))
            combo = surf

        # cache et retour
        self.combo_cache[key] = combo
        return combo
