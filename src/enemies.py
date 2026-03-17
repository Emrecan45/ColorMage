import pygame
import os

from config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT


class Projectile:
    """Projectile tête de mort qui avance horizontalement."""
    def __init__(self, x, y, direction=1, speed=6, size=None):
        self.direction = direction
        self.speed = speed
        self.alive = True

        # Taille projectile
        if size is None:
            self.size = 45
        else:
            self.size = int(size)

        # Charger spritesheet 
        path = resource_path(os.path.join("img", "ennemy.png"))
        self.spritesheet = pygame.image.load(path)
        self.sprite_w = 192
        self.sprite_h = 192

        self.frames = []
        self.collision_boxes = []
        self.masks = [] 
        for col in (0, 1, 2):
            x_sprite = col * self.sprite_w
            y_sprite = 1 * self.sprite_h
            sprite = self.spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_w, self.sprite_h))
            sprite = pygame.transform.scale(sprite, (self.size, self.size))
            mask = pygame.mask.from_surface(sprite)
            flipped_mask = pygame.mask.from_surface(pygame.transform.flip(sprite, True, False))
            box = mask.get_rect()
            if box.w == 0 or box.h == 0:
                box = pygame.Rect(0, 0, self.size, self.size)
            self.frames.append(sprite)
            self.collision_boxes.append(box)
            self.masks.append((mask, flipped_mask))

        self.cache_retournes = {}
        self.cache_explosion_retournes = {}

        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_delay = 100

        self.x = x
        self.y = y
        if self.collision_boxes:
            first_box = self.collision_boxes[0]
        else:
            first_box = pygame.Rect(0, 0, self.size, self.size)
        self.rect = pygame.Rect(int(self.x + first_box.x), int(self.y + first_box.y), int(first_box.w), int(first_box.h))

        self.origin_x = x
        self.collidable = True
        # Explosion animation setup
        self.exploding = False
        self.explosion_frames = []
        self.explosion_index = 0
        self.explosion_last_time = 0
        self.explosion_frame_delay = 120
        for col in (0, 2):
            ex_x = col * self.sprite_w
            ex_y = 2 * self.sprite_h
            ex_sprite = self.spritesheet.subsurface(pygame.Rect(ex_x, ex_y, self.sprite_w, self.sprite_h))
            ex_sprite = pygame.transform.scale(ex_sprite, (self.size, self.size))
            self.explosion_frames.append(ex_sprite)
        # max distance (None = infinite)
        self.max_distance = None

    def update(self):
        # animation
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= self.frame_delay:
            self.last_frame_time = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # déplacement (si pas en explosion)
        if not self.exploding:
            self.x += self.speed * self.direction
        if 0 <= self.frame_index < len(self.collision_boxes):
            box = self.collision_boxes[self.frame_index]
            self.rect.topleft = (int(self.x + box.x), int(self.y + box.y))
            self.rect.size = (int(box.w), int(box.h))
        else:
            self.rect.topleft = (int(self.x), int(self.y))

        # si hors écran, tuer
        if not self.exploding and (self.x < -100 or self.x > 20000):
            self.alive = False

        # Vérifier la portée max
        if not self.exploding and self.max_distance is not None:
            if abs(self.x - self.origin_x) >= self.max_distance:
                # déclencher explosion
                self.start_explosion()

        # Si en explosion, animer l'explosion
        if self.exploding:
            now = pygame.time.get_ticks()
            if now - self.explosion_last_time >= self.explosion_frame_delay:
                self.explosion_last_time = now
                self.explosion_index += 1
                if self.explosion_index >= len(self.explosion_frames):
                    self.alive = False
                    self.exploding = False

    def dessiner(self, ecran):
        if self.exploding and self.explosion_frames:
            frame = self.explosion_frames[self.explosion_index % len(self.explosion_frames)]
            if self.direction == -1:
                cle = ('expl', self.explosion_index % len(self.explosion_frames))
                f = self.cache_explosion_retournes.get(cle)
                if f is None:
                    f = pygame.transform.flip(frame, True, False)
                    self.cache_explosion_retournes[cle] = f
                frame = f
            ecran.blit(frame, (self.x, self.y))
            return
        frame = self.frames[self.frame_index]
        if self.direction == -1:
            cle = ('f', self.frame_index)
            f = self.cache_retournes.get(cle)
            if f is None:
                f = pygame.transform.flip(frame, True, False)
                self.cache_retournes[cle] = f
            frame = f
        ecran.blit(frame, (self.x, self.y))

    def start_explosion(self):
        if not self.explosion_frames:
            self.alive = False
            return
        if self.max_distance is not None:
            if self.direction == 1:
                target_px = self.origin_x + self.max_distance
            else:
                target_px = self.origin_x - self.max_distance
            cell_idx = int(target_px // TAILLE_CELLULE)
            if self.direction == 1:
                edge_x = (cell_idx + 1) * TAILLE_CELLULE
            else:
                edge_x = cell_idx * TAILLE_CELLULE
            self.x = float(edge_x - (self.size // 2))

        self.exploding = True
        self.collidable = False
        self.explosion_index = 0
        self.explosion_last_time = pygame.time.get_ticks()


class Sorcier:
    """Sorcier qui tire des têtes de mort."""
    def __init__(self, x, y, direction=1, shoot_interval=2400, shoot_range_blocks=None):
        self.x = x
        self.y = y
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

        path = resource_path(os.path.join("img", "ennemy.png"))
        self.spritesheet = pygame.image.load(path)
        self.sprite_w = 192
        self.sprite_h = 192

        self.frames = []
        for col in (0, 3):
            x_sprite = col * self.sprite_w
            y_sprite = 0 * self.sprite_h
            sprite = self.spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_w, self.sprite_h))
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            self.frames.append(sprite)

        # Cache pour images retournées du sorcier
        self.cache_retournes = {}

        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
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
        now = pygame.time.get_ticks()
        # Tir uniquement quand l'animation vient d'atteindre la frame de tir
        if self.frame_index == self.firing_frame and self.last_frame_index != self.frame_index:
            return now - self.last_shot >= self.shoot_interval
        return False

    def tirer(self):
        proj_size = 100
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        muzzle_x = int(center_x + (self.width // 2 - proj_size // 2) * self.direction)
        muzzle_y = int(center_y - proj_size // 2)
        proj = Projectile(muzzle_x, muzzle_y, direction=self.direction, size=proj_size)
        # appliquer la portée si fournie
        if self.shoot_range_blocks is not None:
            proj.max_distance = int(self.shoot_range_blocks * TAILLE_CELLULE)
        return proj

    def update(self):
        now = pygame.time.get_ticks()
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
        return proj

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


class Squelette:
    """Squelette qui marche sur N cases, fait demi-tour et attaque tous les 3 pas."""
    def __init__(self, x, y, direction=-1, walk_blocks=3):
        pass
        self.x = x
        self.y = y
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

        path = resource_path(os.path.join("img", "ennemy.png"))
        self.spritesheet = pygame.image.load(path)
        self.sprite_w = 192
        self.sprite_h = 192

        def get_sprite(col, row):
            x_sprite = col * self.sprite_w
            y_sprite = row * self.sprite_h
            sw = self.spritesheet.get_width()
            sh = self.spritesheet.get_height()
            if x_sprite < 0 or y_sprite < 0 or x_sprite + self.sprite_w > sw or y_sprite + self.sprite_h > sh:
                sprite = pygame.Surface((self.sprite_w, self.sprite_h), pygame.SRCALPHA)
                sprite.fill((0, 0, 0, 0))
            else:
                sprite = self.spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_w, self.sprite_h)).copy()
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            return sprite

        # charger les frames d'animation
        self.idle_frame = get_sprite(1, 4)
        self.walk_frames = [get_sprite(2, 4), get_sprite(3, 4)]
        self.pre_attack = get_sprite(4, 4)
        self.attack_frames = []
        for c in range(0, 5):
            self.attack_frames.append(get_sprite(c, 5))

        # si les frames d'attaque sont vides
        all_empty = True
        for f in self.attack_frames:
            br = f.get_bounding_rect()
            if br.w != 0 and br.h != 0:
                all_empty = False
                break
        if all_empty:
            self.attack_frames = [self.pre_attack] * 5

        frames_for_offset = [self.idle_frame] + self.walk_frames + [self.pre_attack] + self.attack_frames
        bottoms = []
        bounds = []
        for f in frames_for_offset:
            br = f.get_bounding_rect()
            bounds.append(br)
            bottoms.append(br.y + br.h)
        if bottoms:
            max_bottom = max(bottoms)
        else:
            max_bottom = 0
        self.frame_offsets = []
        for br in bounds:
            self.frame_offsets.append(max_bottom - (br.y + br.h))

        # hitbox et offset pour chaque frame
        idx = 0
        self.idle_offset = self.frame_offsets[idx]; idx += 1
        self.idle_box = bounds[0]

        self.walk_offsets = []
        self.walk_boxes = []
        for i in range(len(self.walk_frames)):
            self.walk_offsets.append(self.frame_offsets[idx])
            self.walk_boxes.append(bounds[idx])
            idx += 1

        self.pre_attack_offset = self.frame_offsets[idx]
        self.pre_attack_box = bounds[idx]
        idx += 1

        self.attack_offsets = []
        self.attack_boxes = []
        for i in range(len(self.attack_frames)):
            self.attack_offsets.append(self.frame_offsets[idx])
            self.attack_boxes.append(bounds[idx])
            idx += 1

        # calculer les masques de collistion pour chaque frame (pour la cohérence des hitbox avec le visuel)
        def make_masks(surface_list):
            masks = []
            for surf in surface_list:
                mask = pygame.mask.from_surface(surf)
                masks.append((mask, pygame.mask.from_surface(pygame.transform.flip(surf, True, False))))
            return masks

        self.idle_masks = make_masks([self.idle_frame])
        self.walk_masks = make_masks(self.walk_frames)
        self.pre_attack_masks = make_masks([self.pre_attack])
        self.attack_masks = make_masks(self.attack_frames)

        # masque courant + position de dessin utilisés pour les vérifications de collision
        self.current_mask = None
        self.current_draw_x = int(self.x)
        self.current_draw_y = int(self.y)

        # état de l'animation
        self.state = "walking" 
        self.walk_index = 0
        self.last_anim_time = pygame.time.get_ticks()
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
        now = pygame.time.get_ticks()
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
            if not hasattr(self, 'cache_surface_retournes'):
                self.cache_surface_retournes = {}
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


class Slime:
    """Slime qui reste sur place avec animation.
    Vert = 1 PV, Violet = 2 PV.
    Quand le joueur saute dessus : rebond + dégâts au slime
    """
    def __init__(self, x, y, couleur="vert"):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.alive = True

        # PV selon la couleur
        if couleur == "violet":
            self.pv = 2
        else:
            self.pv = 1

        # Charger la spritesheet
        if couleur == "violet":
            chemin = resource_path(os.path.join("img", "slime_violet.png"))
        else:
            chemin = resource_path(os.path.join("img", "slime_vert.png"))
        self.spritesheet = pygame.image.load(chemin)

        # Taille d'un sprite dans la spritesheet
        self.sprite_w = 24
        self.sprite_h = 24

        # Taille d'affichage
        self.taille_affichage = int(TAILLE_CELLULE * 1.5)
        self.y = int(self.y + TAILLE_CELLULE - self.taille_affichage)
        self.x = int(self.x + (TAILLE_CELLULE - self.taille_affichage) / 2)

        # Charger toutes les frames
        self.toutes_frames = []
        for ligne in range(3):
            for col in range(4):
                sx = col * self.sprite_w
                sy = ligne * self.sprite_h
                sprite = self.spritesheet.subsurface(pygame.Rect(sx, sy, self.sprite_w, self.sprite_h))
                sprite = pygame.transform.scale(sprite, (self.taille_affichage, self.taille_affichage))
                self.toutes_frames.append(sprite)

        # Animation : L1C1-4 L2C1-4  L3C1-2 puis inverse
        # Index : 0,1,2,3, 4,5,6,7, 8,9 puis 9,8, 7,6,5,4, 3,2,1,0
        self.sequence_aller = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sequence_retour = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        self.sequence_complete = self.sequence_aller + self.sequence_retour
        self.frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_delay = 120

        # Frame de mort : L3 C3 (index 10)
        self.frame_mort = self.toutes_frames[10]

        # État de mort
        self.en_train_de_mourir = False
        self.mort_timer = 0
        self.mort_duree = 300  # ms

        # Hitbox
        self.rect = pygame.Rect(self.x, self.y, self.taille_affichage, self.taille_affichage)

    def update(self):
        now = pygame.time.get_ticks()

        if self.en_train_de_mourir:
            if now - self.mort_timer >= self.mort_duree:
                self.alive = False
            return

        # Animation continue tant que le slime n'est pas mort
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % len(self.sequence_complete)

        self.rect.topleft = (int(self.x), int(self.y))

    def recevoir_degats(self):
        """Appelée quand le joueur saute sur le slime. Retourne True si le slime meurt."""
        self.pv -= 1
        if self.pv <= 0:
            self.en_train_de_mourir = True
            self.mort_timer = pygame.time.get_ticks()
            return True
        return False

    def dessiner(self, ecran):
        if self.en_train_de_mourir:
            ecran.blit(self.frame_mort, (int(self.x), int(self.y)))
            return

        idx = self.sequence_complete[self.frame_index]
        frame = self.toutes_frames[idx]
        ecran.blit(frame, (int(self.x), int(self.y)))


class Piece:
    """Pièce qui tourne sur elle-même."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

        # Charger la spritesheet de la pièce
        chemin = resource_path(os.path.join("img", "piece.png"))
        self.spritesheet = pygame.image.load(chemin)
        self.sprite_w = 16
        self.sprite_h = 16
        nb_frames = self.spritesheet.get_width() // self.sprite_w

        # Taille d'affichage
        self.taille_affichage = int(TAILLE_CELLULE * 0.7)

        # Charger les frames
        self.frames = []
        for i in range(nb_frames):
            sx = i * self.sprite_w
            sprite = self.spritesheet.subsurface(pygame.Rect(sx, 0, self.sprite_w, self.sprite_h))
            sprite = pygame.transform.scale(sprite, (self.taille_affichage, self.taille_affichage))
            self.frames.append(sprite)

        self.frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_delay = 80

        # Hitbox
        offset = (TAILLE_CELLULE - self.taille_affichage) // 2
        self.draw_x = self.x + offset
        self.draw_y = self.y + offset
        self.rect = pygame.Rect(self.draw_x, self.draw_y, self.taille_affichage, self.taille_affichage)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def dessiner(self, ecran):
        frame = self.frames[self.frame_index]
        ecran.blit(frame, (int(self.draw_x), int(self.draw_y)))


class ProjectileFeu:
    """Projectile de feu tiré par le mage."""
    def __init__(self, x, y, direction=1, speed=VITESSE_DEPLACEMENT):
        self.direction = direction
        self.speed = speed
        self.alive = True
        self.collidable = False  # pas de collision pendant la création

        self.size = 120  # taille d'affichage
        self.hit_size = 40  # taille de la hitbox de collision

        # centre du projectile
        self.centre_x = float(x)
        self.centre_y = float(y)
        self.x = self.centre_x - self.size // 2
        self.y = self.centre_y - self.size // 2

        # création aninmation
        sheet_c = pygame.image.load(resource_path(os.path.join("img", "feu_creation.png"))).convert_alpha()
        self.creation_frames = []
        for i in range(min(10, sheet_c.get_height() // 64)):
            frame = sheet_c.subsurface(pygame.Rect(0, i * 64, 64, 64))
            frame = pygame.transform.scale(frame, (self.size, self.size))
            self.creation_frames.append(frame)

        # trainée
        sheet_t = pygame.image.load(resource_path(os.path.join("img", "feu_trainée.png"))).convert_alpha()
        self.trail_frames = []
        for i in range(sheet_t.get_height() // 64):
            frame = sheet_t.subsurface(pygame.Rect(0, i * 64, 64, 64))
            frame = pygame.transform.scale(frame, (self.size, self.size))
            self.trail_frames.append(frame)
        self.trail_masks = []
        for surf in self.trail_frames:
            self.trail_masks.append(pygame.mask.from_surface(surf))
        self.cache_trail_retourne = {}
        sheet_e = pygame.image.load(resource_path(os.path.join("img", "feu_explosion.png"))).convert_alpha()
        self.explosion_frames = []
        for i in range(sheet_e.get_width() // 64):
            frame = sheet_e.subsurface(pygame.Rect(i * 64, 0, 64, 64))
            frame = pygame.transform.scale(frame, (self.size, self.size))
            self.explosion_frames.append(frame)

        # États : "creation", "trail", "explosion"
        self.state = "creation"
        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.creation_delay = 30
        self.trail_delay = 80
        self.explosion_delay = 60

        self.cache_retourne = {}

        self.rect = pygame.Rect(int(self.centre_x - self.hit_size // 2), int(self.centre_y - self.hit_size // 2),self.hit_size, self.hit_size)

    def update(self):
        now = pygame.time.get_ticks()

        if self.state == "creation":
            if now - self.last_frame_time >= self.creation_delay:
                self.last_frame_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.creation_frames):
                    self.state = "trail"
                    self.frame_index = 0
                    self.collidable = True
        elif self.state == "trail":
            # Déplacement
            self.centre_x += self.speed * self.direction
            if now - self.last_frame_time >= self.trail_delay:
                self.last_frame_time = now
                self.frame_index = (self.frame_index + 1) % len(self.trail_frames)
            # hors écran
            if self.centre_x < -100 or self.centre_x > 2000:
                self.alive = False
        elif self.state == "explosion":
            if now - self.last_frame_time >= self.explosion_delay:
                self.last_frame_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.explosion_frames):
                    self.alive = False

        # mettre a jour les positions de dessin et collision depuis le centre
        self.x = self.centre_x - self.size // 2
        self.y = self.centre_y - self.size // 2
        self.rect.topleft = (int(self.centre_x - self.hit_size // 2), int(self.centre_y - self.hit_size // 2))

    def start_explosion(self):
        self.state = "explosion"
        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.collidable = False

    def get_frame(self):
        if self.state == "creation":
            idx = min(self.frame_index, len(self.creation_frames) - 1)
            return self.creation_frames[idx]
        elif self.state == "trail":
            return self.trail_frames[self.frame_index % len(self.trail_frames)]
        else:
            idx = min(self.frame_index, len(self.explosion_frames) - 1)
            return self.explosion_frames[idx]

    def dessiner(self, ecran):
        frame = self.get_frame()
        if self.direction == -1:
            key = (self.state, self.frame_index)
            f = self.cache_retourne.get(key)
            if f is None:
                f = pygame.transform.flip(frame, True, False)
                self.cache_retourne[key] = f
            frame = f
        draw_y = int(self.y)
        if self.state == "creation":
            draw_y += self.size // 2
        elif self.state == "trail":
            draw_y += 37
        ecran.blit(frame, (int(self.x), draw_y))


class CristalFeu:
    """Cristal de feu qui peut être ramassé par le joueur pour lui donner une capacité de tir ou la restaurer."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

        self.taille_affichage = int(40)  # 75px

        chemin = resource_path(os.path.join("img", "cristal_feu.png"))
        spritesheet = pygame.image.load(chemin).convert()
        spritesheet.set_colorkey((0, 0, 0))

        # Coordonnées de chaque frame dans la spritesheet
        crop_y = 151
        crop_h = 88
        segments = [
            (22,  113),
            (125, 198),
            (215, 265),
            (287, 306),
            (328, 388),
            (402, 473),
            (489, 574),
        ]

        self.nb_frames = len(segments)
        self.frames = []
        cible = self.taille_affichage
        for (x_debut, x_fin) in segments:
            largeur = x_fin - x_debut + 1
            sprite_source = spritesheet.subsurface(pygame.Rect(x_debut, crop_y, largeur, crop_h))
            rapport = min(cible / largeur, cible / crop_h)
            nouvelle_largeur = max(1, int(largeur * rapport))
            nouvelle_hauteur = max(1, int(crop_h * rapport))
            echelle = pygame.transform.scale(sprite_source, (nouvelle_largeur, nouvelle_hauteur))
            # Centrer dans un carré transparent
            res = pygame.Surface((cible, cible), pygame.SRCALPHA)
            res.fill((0, 0, 0, 0))
            decal_x = (cible - nouvelle_largeur) // 2
            decal_y = (cible - nouvelle_hauteur) // 2
            res.blit(echelle, (decal_x, decal_y))
            self.frames.append(res)

        self.frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_delay = 80

        # Pré calculer les masques pour chaque frame
        self.masks = []
        for frame in self.frames:
            mask = pygame.mask.from_surface(frame)
            self.masks.append(mask)
        # position de dessin
        self.current_draw_x = int(self.x - self.taille_affichage // 2)
        self.current_draw_y = int(self.y - self.taille_affichage // 2)
        # masque et rect basés sur la frame de base
        self.current_mask = self.masks[self.frame_index]
        self.rect = pygame.Rect(self.current_draw_x, self.current_draw_y, self.taille_affichage, self.taille_affichage)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % self.nb_frames
        # Mettre à jour la position de dessin et le masque
        draw_x = int(self.x - self.taille_affichage // 2)
        draw_y = int(self.y - self.taille_affichage // 2)
        self.current_draw_x = draw_x
        self.current_draw_y = draw_y
        self.current_mask = self.masks[self.frame_index]
        self.rect.topleft = (draw_x, draw_y)
        self.rect.size = (self.taille_affichage, self.taille_affichage)

    def dessiner(self, ecran):
        frame = self.frames[self.frame_index]
        draw_x = int(self.x - self.taille_affichage // 2)
        draw_y = int(self.y - self.taille_affichage // 2)
        ecran.blit(frame, (draw_x, draw_y))


def mettre_a_jour_groupes(elems):
    for elem in list(elems):
        elem.update()
        try:
            alive = elem.alive
        except AttributeError:
            alive = True
        if not alive:
            elems.remove(elem)


def dessiner_groupes(elems, ecran):
    for elem in elems:
        elem.dessiner(ecran)
