from core import temps
import pygame
import os
import math
import random

from core.config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT, LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import charger_image
from entities.projectiles import ProjectileDemon


cache_projectile = {}


import math
from core.config import TAILLE_CELLULE
from entities.projectiles import Projectile

cache_sorcier = {}


def construire_frames_sorcier(width, height):
    cle = (width, height)
    if cle in cache_sorcier:
        return cache_sorcier[cle]
    sprite_w = 192
    sprite_h = 192
    sheet = charger_image(resource_path(os.path.join("assets/img/entities", "ennemy.png")), "alpha")
    frames = []
    for col in (0, 3):
        sprite = sheet.subsurface(pygame.Rect(col * sprite_w, 0, sprite_w, sprite_h))
        frames.append(pygame.transform.scale(sprite, (width, height)))
    cache_sorcier[cle] = frames
    return frames


cache_sorcier_masks = {}

def construire_masques_sorcier(width, height):
    cle = (width, height)
    if cle not in cache_sorcier_masks:
        cache_sorcier_masks[cle] = construire_masques(construire_frames_sorcier(width, height))
    return cache_sorcier_masks[cle]


class Sorcier:
    """Sorcier qui tire des têtes de mort."""

    def __init__(self, x, y, direction=1, shoot_interval=2400, shoot_range_blocks=None):
        self.x = x
        self.y = y
        self.visual_x = None
        self.visual_y = None
        self.direction = direction
        self.shoot_interval = int(shoot_interval)
        if shoot_range_blocks is not None:
            self.shoot_range_blocks = int(shoot_range_blocks)
        else:
            self.shoot_range_blocks = None
        self.last_shot = 0
        self.alive = True

        # Taille du sorcier (utiliser 2 cellules comme joueur)
        self.width = TAILLE_CELLULE * 2
        self.height = TAILLE_CELLULE * 2
        # Hitbox identique au joueur
        self.marge_x = 40
        self.marge_y_haut = 10
        self.marge_y_bas = 2
        self.rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut,
                                self.width - 2 * self.marge_x,
                                self.height - self.marge_y_haut - self.marge_y_bas)

        # Frames partagées (construites une seule fois)
        self.frames = construire_frames_sorcier(self.width, self.height)
        self.masks = construire_masques_sorcier(self.width, self.height)

        # Cache pour images retournées du sorcier
        self.cache_retournes = {}
        self.current_mask = None
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

        self.frame_index = 0
        self.last_frame_time = temps.obtenir_temps()
        self.firing_frame = 1
        n = max(1, len(self.frames))
        # durée courte pour la frame de tir
        firing_ms = max(60, int(self.shoot_interval * 0.12))
        remaining = max(0, self.shoot_interval - firing_ms)
        if n > 1:
            other_ms = int(remaining / max(1, n - 1))
        else:
            other_ms = remaining
        # créer la liste de délais par frame
        self.frame_delays = []
        for i in range(n):
            if i == self.firing_frame:
                self.frame_delays.append(firing_ms)
            else:
                self.frame_delays.append(max(60, other_ms))
        self.frame_delay = self.frame_delays[0]
        self.last_frame_index = self.frame_index

        self.firing = False
        self.firing_duration = None

    def peut_tirer(self):
        now = temps.obtenir_temps()
        # Tir uniquement quand l'animation vient d'atteindre la frame de tir
        if self.frame_index == self.firing_frame and self.last_frame_index != self.frame_index:
            return now - self.last_shot >= self.shoot_interval
        return False

    def tirer(self):
        proj_size = 100
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        muzzle_x = int(center_x + (self.width // 2) * self.direction - proj_size // 2)
        muzzle_y = int(center_y - proj_size // 2)
        proj = Projectile(muzzle_x, muzzle_y, direction=self.direction, size=proj_size)
        # appliquer la portée si fournie
        if self.shoot_range_blocks is not None:
            proj.max_distance = int(self.shoot_range_blocks * TAILLE_CELLULE)
        return proj

    def update(self):
        now = temps.obtenir_temps()
        prev_frame = self.frame_index
        proj = None
        # Si on n'est pas en animation de tir et le cooldown est écoulé, déclencher le tir
        if not self.firing and now - self.last_shot >= self.shoot_interval:
            # lancer l'animation de tir
            self.firing = True
            self.firing_start_time = now
            # mettre la frame de tir
            self.frame_index = self.firing_frame
            proj = self.tirer()
            self.last_shot = now
        elif self.firing:
            # si en animation de tir, vérifier durée
            if self.firing_duration is None:
                self.firing_duration = max(80, int(self.shoot_interval * 0.12))
            if now - self.firing_start_time >= self.firing_duration:
                # revenir à la frame initiale
                self.firing = False
                self.frame_index = 0

        self.last_frame_index = prev_frame
        self.rect.topleft = (int(self.x + self.marge_x), int(self.y + self.marge_y_haut))
        self.maj_mask_courant()
        return proj

    def maj_mask_courant(self):
        mask_pair = self.masks[self.frame_index % len(self.masks)]
        if self.direction == -1:
            self.current_mask = mask_pair[1]
        else:
            self.current_mask = mask_pair[0]
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

    def dessiner(self, ecran):
        frame = self.frames[self.frame_index]
        if self.direction == -1:
            cle = ('f', self.frame_index)
            f = self.cache_retournes.get(cle)
            if f is None:
                f = pygame.transform.flip(frame, True, False)
                self.cache_retournes[cle] = f
            frame = f

        ecran.blit(frame, (self.x, self.y))
        self.maj_mask_courant()


def construire_masques(surface_list):
    masques = []
    for surf in surface_list:
        mask = pygame.mask.from_surface(surf)
        mask_flip = pygame.mask.from_surface(pygame.transform.flip(surf, True, False))
        masques.append((mask, mask_flip))
    return masques


# Frames/offsets/masques du squelette, construits une seule fois
cache_squelette = {}


def construire_assets_squelette(width, height):
    """Construit une seule fois les frames, offsets, boîtes et masques du squelette."""
    cle = (width, height)
    if cle in cache_squelette:
        return cache_squelette[cle]

    sprite_w = 192
    sprite_h = 192
    sheet = charger_image(resource_path(os.path.join("assets/img/entities", "ennemy.png")), "alpha")

    def get_sprite(col, row):
        x_sprite = col * sprite_w
        y_sprite = row * sprite_h
        sw = sheet.get_width()
        sh = sheet.get_height()
        if x_sprite < 0 or y_sprite < 0 or x_sprite + sprite_w > sw or y_sprite + sprite_h > sh:
            sprite = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
            sprite.fill((0, 0, 0, 0))
        else:
            sprite = sheet.subsurface(pygame.Rect(x_sprite, y_sprite, sprite_w, sprite_h)).copy()
        return pygame.transform.scale(sprite, (width, height))

    idle_frame = get_sprite(1, 4)
    walk_frames = [get_sprite(2, 4), get_sprite(3, 4)]
    pre_attack = get_sprite(4, 4)
    attack_frames = []
    for c in range(0, 5):
        attack_frames.append(get_sprite(c, 5))

    # si toutes les frames d'attaque sont vides, on garde la frame pre_attack
    all_empty = True
    for f in attack_frames:
        box = f.get_bounding_rect()
        if box.w != 0 and box.h != 0:
            all_empty = False
    if all_empty:
        attack_frames = [pre_attack] * 5

    frames_for_offset = [idle_frame] + walk_frames + [pre_attack] + attack_frames
    bounds = []
    for f in frames_for_offset:
        bounds.append(f.get_bounding_rect())
    bottoms = []
    for br in bounds:
        bottoms.append(br.y + br.h)
    if bottoms:
        max_bottom = max(bottoms)
    else:
        max_bottom = 0
    frame_offsets = []
    for br in bounds:
        frame_offsets.append(max_bottom - (br.y + br.h))

    idx = 0
    idle_offset = frame_offsets[idx]
    idle_box = bounds[idx]
    idx += 1
    walk_offsets = []
    walk_boxes = []
    for i in range(len(walk_frames)):
        walk_offsets.append(frame_offsets[idx])
        walk_boxes.append(bounds[idx])
        idx += 1
    pre_attack_offset = frame_offsets[idx]
    pre_attack_box = bounds[idx]
    idx += 1
    attack_offsets = []
    attack_boxes = []
    for i in range(len(attack_frames)):
        attack_offsets.append(frame_offsets[idx])
        attack_boxes.append(bounds[idx])
        idx += 1

    cache_squelette[cle] = {
        "idle_frame": idle_frame, "walk_frames": walk_frames,
        "pre_attack": pre_attack, "attack_frames": attack_frames,
        "idle_offset": idle_offset, "idle_box": idle_box,
        "walk_offsets": walk_offsets, "walk_boxes": walk_boxes,
        "pre_attack_offset": pre_attack_offset, "pre_attack_box": pre_attack_box,
        "attack_offsets": attack_offsets, "attack_boxes": attack_boxes,
        "idle_masks": construire_masques([idle_frame]), "walk_masks": construire_masques(walk_frames),
        "pre_attack_masks": construire_masques([pre_attack]), "attack_masks": construire_masques(attack_frames),
    }
    return cache_squelette[cle]


class Squelette:
    """Squelette qui marche sur N cases, fait demi-tour et attaque tous les 3 pas."""

    def __init__(self, x, y, direction=-1, walk_blocks=3):
        self.x = x
        self.y = y
        self.visual_x = self.x
        self.visual_y = self.y
        self.direction = direction
        self.alive = True

        self.width = TAILLE_CELLULE * 2
        self.height = TAILLE_CELLULE * 2
        self.marge_x = 40
        self.marge_y_haut = 10
        self.marge_y_bas = 2
        self.rect = pygame.Rect(self.x + self.marge_x, self.y + self.marge_y_haut,
                                self.width - 2 * self.marge_x,
                                self.height - self.marge_y_haut - self.marge_y_bas)

        # Frames/offsets/masques partagés (construits une seule fois)
        a = construire_assets_squelette(self.width, self.height)
        self.idle_frame = a["idle_frame"]
        self.walk_frames = a["walk_frames"]
        self.pre_attack = a["pre_attack"]
        self.attack_frames = a["attack_frames"]
        self.idle_offset = a["idle_offset"]
        self.idle_box = a["idle_box"]
        self.walk_offsets = a["walk_offsets"]
        self.walk_boxes = a["walk_boxes"]
        self.pre_attack_offset = a["pre_attack_offset"]
        self.pre_attack_box = a["pre_attack_box"]
        self.attack_offsets = a["attack_offsets"]
        self.attack_boxes = a["attack_boxes"]
        self.idle_masks = a["idle_masks"]
        self.walk_masks = a["walk_masks"]
        self.pre_attack_masks = a["pre_attack_masks"]
        self.attack_masks = a["attack_masks"]

        # masque courant + position de dessin utilisés pour les vérifications de collision
        self.current_mask = None
        self.cache_surface_retournes = {}
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

        # état de l'animation
        self.state = "walking"
        self.walk_index = 0
        self.last_anim_time = temps.obtenir_temps()
        self.walk_delay = 180
        self.pre_attack_delay = 140
        self.attack_delay = 120

        # mouvement
        self.speed = 2
        self.origin_x = x
        if walk_blocks is not None:
            self.walk_blocks = int(walk_blocks)
        else:
            self.walk_blocks = 3
        self.max_distance = self.walk_blocks * TAILLE_CELLULE
        self.turn_start_time = 0
        self.turn_pause_ms = 240

        # conteur de pas pour déclencher l'attaque
        self.step_count = 0
        self.prev_walk_index = self.walk_index

        # état d'attaque
        self.attacking = False
        self.attack_index = 0
        self.attack_start_time = 0
        self.pre_attack_start = 0

    def update(self):
        now = temps.obtenir_temps()
        if self.state == "attacking":
            if now - self.last_anim_time >= self.attack_delay:
                self.last_anim_time = now
                self.attack_index += 1
                if self.attack_index >= len(self.attack_frames):
                    # fin de l'attaque
                    self.attacking = False
                    self.attack_index = 0
                    self.step_count = 0
                    self.state = "walking"
            # pas de mouvement pendant l'attaque

        elif self.state == "pre_attack":
            if now - self.pre_attack_start >= self.pre_attack_delay:
                self.state = "attacking"
                self.attacking = True
                self.attack_index = 0
                self.last_anim_time = now

        elif self.state == "turning":
            if now - self.turn_start_time >= self.turn_pause_ms:
                self.state = "walking"
                self.direction *= -1

        else: 
            # marche : animer les pas
            if now - self.last_anim_time >= self.walk_delay:
                self.last_anim_time = now
                prev = self.walk_index
                self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
                # compter chaque pas
                if self.walk_index != prev:
                    self.step_count += 1
                # tous les 3 pas déclencher lattaque
                if self.step_count >= 3:
                    self.state = "pre_attack"
                    self.pre_attack_start = now
                    self.last_anim_time = now

            # déplacer horizontalement lors de la marche
            if self.state == "walking":
                self.x += self.speed * self.direction

                # vérifier la distance parcourue
                if abs(self.x - self.origin_x) >= self.max_distance:
                    # commencer à tourner
                    self.state = "turning"
                    self.turn_start_time = now

        if self.state == "attacking":
            idx = self.attack_index % len(self.attack_boxes)
            box = self.attack_boxes[idx]
            offset = self.attack_offsets[idx]
        elif self.state == "pre_attack":
            box = self.pre_attack_box
            offset = self.pre_attack_offset
        elif self.state == "walking":
            box = self.walk_boxes[self.walk_index]
            offset = self.walk_offsets[self.walk_index]
        else:
            box = self.idle_box
            offset = self.idle_offset

        draw_y = self.y + offset
        self.rect.topleft = (int(self.x + box.x), int(draw_y + box.y))
        self.rect.size = (int(box.w), int(box.h))

    def dessiner(self, ecran):
        # choisir la frame
        if self.state == "attacking":
            idx = self.attack_index % len(self.attack_frames)
            frame = self.attack_frames[idx]
            offset = self.attack_offsets[idx]
        elif self.state == "pre_attack":
            frame = self.pre_attack
            offset = self.pre_attack_offset
        elif self.state == "turning":
            frame = self.idle_frame
            offset = self.idle_offset
        elif self.state == "walking":
            frame = self.walk_frames[self.walk_index]
            offset = self.walk_offsets[self.walk_index]
        else:
            frame = self.idle_frame
            offset = self.idle_offset

        flipped = False
        draw_frame = frame
        if self.direction == -1:
            # utiliser un cache basé sur l'etat et l'indice de frame
            if self.state == "attacking":
                key = ("att", self.attack_index % max(1, len(self.attack_frames)))
            elif self.state == "pre_attack":
                key = ("pre", 0)
            elif self.state == "walking":
                key = ("walk", self.walk_index)
            elif self.state == "turning":
                key = ("idle", 0)
            else:
                key = ("idle", 0)
            cached = self.cache_surface_retournes.get(key)
            if cached is None:
                cached = pygame.transform.flip(frame, True, False)
                self.cache_surface_retournes[key] = cached
            draw_frame = cached
            flipped = True
        draw_x = int(self.x)
        draw_y = int(self.y + offset)
        ecran.blit(draw_frame, (draw_x, draw_y))

        # mettre à jour le masque de collision courant et sa position de dessin pour les vérifications de collision
        self.current_draw_x = draw_x
        self.current_draw_y = draw_y
        if self.state == "attacking":
            idx = self.attack_index % len(self.attack_masks)
            mask_pair = self.attack_masks[idx]
        elif self.state == "pre_attack":
            mask_pair = self.pre_attack_masks[0]
        elif self.state == "walking":
            mask_pair = self.walk_masks[self.walk_index]
        else:
            mask_pair = self.idle_masks[0]
        if flipped:
            self.current_mask = mask_pair[1]
        else:
            self.current_mask = mask_pair[0]


# Frames du slime, construites une seule fois par couleur

cache_slime = {}


def construire_frames_slime(couleur, taille_affichage):
    if couleur in cache_slime:
        return cache_slime[couleur]
    sprite_w = 24
    sprite_h = 24
    if couleur == "violet":
        chemin = resource_path(os.path.join("assets/img/entities", "slime_violet.png"))
    else:
        chemin = resource_path(os.path.join("assets/img/entities", "slime_vert.png"))
    sheet = charger_image(chemin, "alpha")
    frames = []
    for ligne in range(3):
        for col in range(4):
            sprite = sheet.subsurface(pygame.Rect(col * sprite_w, ligne * sprite_h, sprite_w, sprite_h))
            frames.append(pygame.transform.scale(sprite, (taille_affichage, taille_affichage)))
    cache_slime[couleur] = frames
    return frames


class Slime:
    """Slime qui reste sur place avec animation.
    Vert = 1 PV, Violet = 2 PV.
    Quand le joueur saute dessus : rebond + dégâts au slime
    """

    def __init__(self, x, y, couleur="vert"):
        self.x = x
        self.y = y
        self.visual_x = None
        self.visual_y = None
        self.couleur = couleur
        self.alive = True

        # PV selon la couleur
        if couleur == "violet":
            self.pv = 2
        else:
            self.pv = 1

        # Taille d'affichage
        self.taille_affichage = int(TAILLE_CELLULE * 1.5)
        self.y = int(self.y + TAILLE_CELLULE - self.taille_affichage)
        self.x = int(self.x + (TAILLE_CELLULE - self.taille_affichage) / 2)

        # Frames partagées (construites une seule fois par couleur)
        self.toutes_frames = construire_frames_slime(self.couleur, self.taille_affichage)

        # Animation : L1C1-4 L2C1-4  L3C1-2 puis inverse
        # Index : 0,1,2,3, 4,5,6,7, 8,9 puis 9,8, 7,6,5,4, 3,2,1,0
        self.sequence_aller = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sequence_retour = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        self.sequence_complete = self.sequence_aller + self.sequence_retour
        self.anim_delay = 120
        self.frame_index = random.randint(0, len(self.sequence_complete) - 1)
        decalage_anim = random.randint(0, self.anim_delay)
        self.last_anim_time = temps.obtenir_temps() - decalage_anim

        # Frame de mort : L3 C3 (index 10) - flash rouge réservé à la mort
        self.frame_mort = self.toutes_frames[10]
        # Frame de douleur : L3 C4 (index 11) - animation quand il prend un coup sans mourir
        if len(self.toutes_frames) > 11:
            self.frame_douleur = self.toutes_frames[11]
        else:
            self.frame_douleur = self.toutes_frames[10]

        # État de mort
        self.en_train_de_mourir = False
        self.mort_timer = 0
        self.mort_duree = 300  # ms

        # État de douleur (coup encaissé sans mourir - slime violet)
        self.en_douleur = False
        self.douleur_timer = 0
        self.douleur_duree = 350  # ms

        # Hitbox
        echelle_hb = self.taille_affichage / 24.0
        self.marge_x_hitbox = round(5 * echelle_hb)
        self.decalage_y_hitbox = 20
        largeur_hitbox = round(14 * echelle_hb)
        self.rect = pygame.Rect(
            int(self.x) + self.marge_x_hitbox,
            int(self.y) + self.decalage_y_hitbox,
            largeur_hitbox,
            self.taille_affichage - self.decalage_y_hitbox,
        )

    def update(self):
        now = temps.obtenir_temps()

        if self.en_train_de_mourir:
            if now - self.mort_timer >= self.mort_duree:
                self.alive = False
            return

        # Fin de l'animation de douleur -> retour à l'animation normale
        if self.en_douleur:
            if now - self.douleur_timer >= self.douleur_duree:
                self.en_douleur = False
            else:
                self.rect.topleft = (int(self.x) + self.marge_x_hitbox, int(self.y) + self.decalage_y_hitbox)
                return

        # Animation continue tant que le slime n'est pas mort
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % len(self.sequence_complete)

        self.rect.topleft = (int(self.x) + self.marge_x_hitbox, int(self.y) + self.decalage_y_hitbox)

    def recevoir_degats(self):
        """Appelée quand le joueur saute sur le slime. Retourne True si le slime meurt."""
        self.pv -= 1
        if self.pv <= 0:
            self.en_train_de_mourir = True
            self.mort_timer = temps.obtenir_temps()
            return True
        # Coup encaissé sans mourir : animation de douleur (sans le rouge)
        self.en_douleur = True
        self.douleur_timer = temps.obtenir_temps()
        return False

    def dessiner(self, ecran):
        if self.en_train_de_mourir:
            ecran.blit(self.frame_mort, (int(self.x), int(self.y)))
            return

        if self.en_douleur:
            ecran.blit(self.frame_douleur, (int(self.x), int(self.y)))
            return

        idx = self.sequence_complete[self.frame_index]
        frame = self.toutes_frames[idx]
        ecran.blit(frame, (int(self.x), int(self.y)))


cache_demon = {}

DEMON_W = int(TAILLE_CELLULE * 2.1)
DEMON_H = int(DEMON_W * 69 / 79)

def construire_assets_demon(width, height):
    """Découpe les spritesheets du démon (idle/vol/attaque/dégât/mort)."""
    cle = (width, height)
    if cle in cache_demon:
        return cache_demon[cle]

    def decouper(nom, nb_frames):
        chemin = resource_path(os.path.join("assets/img/entities", nom))
        sheet = charger_image(chemin, "alpha")
        fw = sheet.get_width() // nb_frames
        fh = sheet.get_height()
        frames = []
        for i in range(nb_frames):
            sprite = sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh))
            frames.append(pygame.transform.scale(sprite, (width, height)))
        return frames

    idle = decouper("demon_idle.png", 4)
    vol = decouper("demon_vol.png", 4)
    attaque = decouper("demon_attaque.png", 8)
    degat = decouper("demon_degat.png", 4)
    mort = decouper("demon_mort.png", 7)
    assets = {
        "idle": idle, "vol": vol, "attaque": attaque, "degat": degat, "mort": mort,
        # Masques pour chaque frame
        "masks_idle": construire_masques(idle),
        "masks_vol": construire_masques(vol),
        "masks_attaque": construire_masques(attaque),
        "masks_degat": construire_masques(degat),
        "masks_mort": construire_masques(mort),
    }
    cache_demon[cle] = assets
    return assets


class Demon:
    """Démon volant. Toutes les 3 secondes, fonce ou tire sur le joueur. 3 PV.
    """

    PV_MAX = 3
    INTERVALLE_CHARGE = 3000  # ms entre deux actions
    TIR_FRAME = 4

    def __init__(self, x, y):
        self.width = DEMON_W
        self.height = DEMON_H

        # position de base
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.visual_x = None
        self.visual_y = None

        self.pv = self.PV_MAX
        self.alive = True
        self.direction = 1  # 1 = regarde à droite -1 = à gauche

        a = construire_assets_demon(self.width, self.height)
        self.frames_idle = a["idle"]
        self.frames_vol = a["vol"]
        self.frames_attaque = a["attaque"]
        self.frames_degat = a["degat"]
        self.frames_mort = a["mort"]
        self.masks_idle = a["masks_idle"]
        self.masks_vol = a["masks_vol"]
        self.masks_attaque = a["masks_attaque"]
        self.masks_degat = a["masks_degat"]
        self.masks_mort = a["masks_mort"]
        self.cache_flip = {}
        self.current_mask = None
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

        # hitbox
        self.marge_x = int(self.width * 0.18)
        self.marge_y_haut = int(self.height * 0.15)
        frames_pour_marge = self.frames_vol + self.frames_attaque + self.frames_idle
        bas_sprite = 0
        for frame in frames_pour_marge:
            bas = frame.get_bounding_rect().bottom
            if bas > bas_sprite:
                bas_sprite = bas
        self.marge_y_bas = self.height - bas_sprite
        if self.marge_y_bas < 0:
            self.marge_y_bas = 0
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.maj_rect()

        # animation
        self.state = "vol"  # vol charge retour
        self.anim_delay = 90
        self.frame_index = random.randint(0, len(self.frames_vol) - 1)
        decalage_anim = random.randint(0, self.anim_delay)
        self.last_anim = temps.obtenir_temps() - decalage_anim

        # charge
        decalage_charge = random.randint(0, int(self.INTERVALLE_CHARGE * 0.7))
        self.last_charge = temps.obtenir_temps() - decalage_charge
        self.charge_vx = 0.0
        self.charge_vy = 0.0
        self.charge_dist = 0.0
        self.charge_max_dist = TAILLE_CELLULE * 6
        self.vitesse_charge = 13.0

        # avant la charge
        self.prepare_duree = 420  # ms
        self.prepare_start = 0
        self.prepare_x0 = 0.0
        self.prepare_y0 = 0.0
        self.recoil = TAILLE_CELLULE * 0.5

        # pattern : tir, charge, tir, charge...
        self.prochaine_action = "tir"
        self.a_tire = False

        # animation de dégât
        self.degat_actif = False
        self.degat_index = 0
        self.degat_timer = 0

        # mort
        self.en_train_de_mourir = False
        self.mort_index = 0
        self.mort_timer = 0

        self.bob_phase = random.uniform(0, 2 * math.pi)
        self.bob_amplitude = TAILLE_CELLULE * 0.25

    def maj_rect(self):
        self.rect = pygame.Rect(
            int(self.x + self.marge_x), int(self.y + self.marge_y_haut),
            self.width - 2 * self.marge_x,
            self.height - self.marge_y_haut - self.marge_y_bas,
        )

    def demarrer_charge(self, joueur):
        """Vise la position actuelle du joueur et lance une charge en ligne droite."""
        cible_x = joueur.x + joueur.largeur / 2
        cible_y = joueur.y + joueur.hauteur / 2
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        dx = cible_x - cx
        dy = cible_y - cy
        dist = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        self.charge_vx = math.cos(ang) * self.vitesse_charge
        self.charge_vy = math.sin(ang) * self.vitesse_charge
        self.charge_dist = 0.0
        self.charge_max_dist = max(TAILLE_CELLULE * 2, min(dist + TAILLE_CELLULE * 1.5, TAILLE_CELLULE * 10))
        if self.charge_vx < 0:
            self.direction = -1
        else:
            self.direction = 1
        self.state = "charge"
        self.frame_index = 0
        self.last_anim = temps.obtenir_temps()

    def demarrer_tir(self, joueur):
        """Se tourne vers le joueur et lance l'animation d'attaque (tir)."""
        cible_x = joueur.x + joueur.largeur / 2
        cx = self.x + self.width / 2
        if cible_x < cx:
            self.direction = -1
        else:
            self.direction = 1
        self.state = "tir"
        self.frame_index = 0
        self.a_tire = False
        self.last_anim = temps.obtenir_temps()

    def creer_projectile(self, joueur):
        """Crée un projectile dirigé vers le joueur, depuis le centre du démon."""
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        cible_x = joueur.x + joueur.largeur / 2
        cible_y = joueur.y + joueur.hauteur / 2
        dx = cible_x - cx
        dy = cible_y - cy
        dist = max(1.0, math.hypot(dx, dy))
        vx = dx / dist * ProjectileDemon.VITESSE
        vy = dy / dist * ProjectileDemon.VITESSE
        return ProjectileDemon(cx, cy, vx, vy)

    def recevoir_degats(self, degats=1):
        """Encaisse un tir. Retourne True si le démon vient de mourir."""
        if self.en_train_de_mourir:
            return False
        self.pv -= degats
        if self.pv <= 0:
            self.en_train_de_mourir = True
            self.mort_index = 0
            self.mort_timer = temps.obtenir_temps()
            return True
        self.degat_actif = True
        self.degat_index = 0
        self.degat_timer = temps.obtenir_temps()
        return False

    def touche_mur(self, niveau, couleur):
        """True si la hitbox courante chevauche un mur solide pour la couleur du mage."""
        if niveau is None or couleur is None:
            return False
        self.maj_rect()
        return niveau.collision(self.rect, couleur)

    def terminer_charge(self, now):
        """Termine la charge : le démon reste là où il est arrivé."""
        self.base_x = self.x
        self.base_y = self.y
        self.bob_phase = -now * 0.004
        self.state = "vol"
        self.last_charge = now
        self.frame_index = 0

    def update(self, joueur=None, niveau=None, passif=False):
        now = temps.obtenir_temps()
        couleur = None
        if joueur is not None:
            couleur = joueur.couleur
        projectile = None  # renvoyé à main.py quand le démon tire

        # passif
        if passif and self.state in ("prepare", "charge"):
            self.terminer_charge(now)

        # Animation de mort
        if self.en_train_de_mourir:
            if now - self.mort_timer >= self.anim_delay:
                self.mort_timer = now
                self.mort_index += 1
                if self.mort_index >= len(self.frames_mort):
                    self.mort_index = len(self.frames_mort) - 1
                    self.alive = False
            self.maj_rect()
            return

        # Animation de dégât
        if self.degat_actif and now - self.degat_timer >= self.anim_delay:
            self.degat_timer = now
            self.degat_index += 1
            if self.degat_index >= len(self.frames_degat):
                self.degat_actif = False
                self.degat_index = 0

        if not passif and joueur is not None:
            centre_j = joueur.x + joueur.largeur / 2
            if centre_j < (self.x + self.width / 2):
                self.direction = -1
            else:
                self.direction = 1

        # état
        if self.state == "vol":
            old_y = self.y
            self.y = self.base_y + math.sin(now * 0.004 + self.bob_phase) * self.bob_amplitude
            if self.touche_mur(niveau, couleur):
                self.y = old_y  # ne pas s'enfoncer dans un mur en flottant
            if not passif and joueur is not None and now - self.last_charge >= self.INTERVALLE_CHARGE:
                # alterne tir puis charge
                if self.prochaine_action == "tir":
                    self.prochaine_action = "charge"
                    self.demarrer_tir(joueur)
                else:
                    self.prochaine_action = "tir"
                    self.state = "prepare"
                    self.prepare_start = now
                    self.prepare_x0 = self.x
                    self.prepare_y0 = self.y
                    self.frame_index = 0
                    # son de charge
                    if niveau is not None:
                        niveau.son_demon_fonce.play()

        elif self.state == "tir":
            # joue l'animation d'attaque et lâche le projectile à une frame précise
            if joueur is not None and not self.a_tire and self.frame_index >= self.TIR_FRAME:
                self.a_tire = True
                projectile = self.creer_projectile(joueur)
            if self.frame_index >= len(self.frames_attaque) - 1:
                self.state = "vol"
                self.last_charge = now
                self.base_x = self.x
                self.base_y = self.y

        elif self.state == "prepare":
            # petit recul vers l'arrière pour prévenir le joueur
            old_x = self.x
            t = min(1.0, (now - self.prepare_start) / self.prepare_duree)
            self.x = self.prepare_x0 - self.direction * self.recoil * math.sin(t * math.pi)
            if self.touche_mur(niveau, couleur):
                self.x = old_x  # bloqué par un mur dans son recul
            if now - self.prepare_start >= self.prepare_duree:
                if joueur is not None:
                    self.demarrer_charge(joueur)
                else:
                    self.state = "vol"
                    self.last_charge = now

        elif self.state == "charge":
            depart_x = self.x
            depart_y = self.y

            # Déplacement horizontal
            self.x += self.charge_vx
            if self.touche_mur(niveau, couleur):
                self.x = depart_x

            # Déplacement vertical
            self.y += self.charge_vy
            if self.touche_mur(niveau, couleur):
                self.y = depart_y

            self.charge_dist += math.hypot(self.charge_vx, self.charge_vy)
            if self.charge_dist >= self.charge_max_dist:
                self.terminer_charge(now)

        # Une plateforme qui rentre dans le démon le pousse
        if niveau is not None and couleur is not None:
            niveau.pousser_demon_par_plateformes(self, couleur)

        # Empêcher le démon de sortir de l'écran sur les côtés
        hitbox_gauche = self.x + self.marge_x
        hitbox_droite = self.x + self.width - self.marge_x
        if hitbox_gauche < 0:
            self.x = -self.marge_x
        if hitbox_droite > LARGEUR_ECRAN:
            self.x = LARGEUR_ECRAN - self.width + self.marge_x

        # Avancer l'animation courante
        self.animer()

        self.maj_rect()
        self.maj_mask_courant()
        return projectile

    def animer(self):
        """Avance l'animation courante (sans déplacement)."""
        now = temps.obtenir_temps()
        if now - self.last_anim >= self.anim_delay:
            self.last_anim = now
            self.frame_index += 1

    def passer_en_idle(self):
        """Remet le démon en vol (idle)."""
        if not self.en_train_de_mourir:
            self.state = "vol"

    def decaler_ancres(self, dx, dy):
        """Décale les positions de référence (vol et prepare) quand on pousse le démon."""
        self.base_x += dx
        self.base_y += dy
        self.prepare_x0 += dx
        self.prepare_y0 += dy

    def frame_courante(self):
        """Retourne (frame, paire_de_masques) selon l'état/anim."""
        if self.en_train_de_mourir:
            idx = min(self.mort_index, len(self.frames_mort) - 1)
            return self.frames_mort[idx], self.masks_mort[idx]
        if self.degat_actif:
            idx = self.degat_index % len(self.frames_degat)
            return self.frames_degat[idx], self.masks_degat[idx]
        if self.state == "charge":
            idx = self.frame_index % len(self.frames_attaque)
            return self.frames_attaque[idx], self.masks_attaque[idx]
        if self.state == "tir":
            idx = min(self.frame_index, len(self.frames_attaque) - 1)
            return self.frames_attaque[idx], self.masks_attaque[idx]
        if self.state == "prepare":
            idx = self.frame_index % len(self.frames_idle)
            return self.frames_idle[idx], self.masks_idle[idx]
        idx = self.frame_index % len(self.frames_vol)
        return self.frames_vol[idx], self.masks_vol[idx]

    def maj_mask_courant(self):
        """Met à jour le masque courant et sa position de dessin."""
        paire = self.frame_courante()
        mask_pair = paire[1]
        if self.direction == 1:
            self.current_mask = mask_pair[1]
        else:
            self.current_mask = mask_pair[0]
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

    def oriente(self, frame):
        """Retourne le sprite (mis en cache) selon la direction.
        """
        if self.direction == 1:
            f = self.cache_flip.get(frame)
            if f is None:
                f = pygame.transform.flip(frame, True, False)
                self.cache_flip[frame] = f
            return f
        return frame

    def dessiner(self, ecran):
        paire = self.frame_courante()
        frame = paire[0]
        ecran.blit(self.oriente(frame), (int(self.x), int(self.y)))
        self.maj_mask_courant()
