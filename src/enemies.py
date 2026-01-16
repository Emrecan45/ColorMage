import pygame
import os

from config import TAILLE_CELLULE


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
        path = os.path.join("img", "ennemy.png")
        self.spritesheet = pygame.image.load(path)
        self.sprite_w = 192
        self.sprite_h = 196

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

        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_delay = 100

        self.x = x
        self.y = y
        first_box = self.collision_boxes[0] if self.collision_boxes else pygame.Rect(0, 0, self.size, self.size)
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
            ecran.blit(frame, (self.x, self.y))
            return
        frame = self.frames[self.frame_index]
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)
        ecran.blit(frame, (self.x, self.y))

    def start_explosion(self):
        if not self.explosion_frames:
            self.alive = False
            return
        if self.max_distance is not None:
            target_px = self.origin_x + (self.max_distance if self.direction == 1 else -self.max_distance)
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

        path = os.path.join("img", "ennemy.png")
        self.spritesheet = pygame.image.load(path)
        self.sprite_w = 192
        self.sprite_h = 196

        self.frames = []
        for col in (0, 3):
            x_sprite = col * self.sprite_w
            y_sprite = 0 * self.sprite_h
            sprite = self.spritesheet.subsurface(pygame.Rect(x_sprite, y_sprite, self.sprite_w, self.sprite_h))
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            self.frames.append(sprite)

        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.firing_frame = 1
        n = max(1, len(self.frames))
        # durée courte pour la frame de tir
        firing_ms = max(60, int(self.shoot_interval * 0.12))
        remaining = max(0, self.shoot_interval - firing_ms)
        other_ms = int(remaining / max(1, n - 1)) if n > 1 else remaining
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
            frame = pygame.transform.flip(frame, True, False)
        ecran.blit(frame, (self.x, self.y))


def mettre_a_jour_groupes(elems):
    for elem in list(elems):
        elem.update()
        if not getattr(elem, "alive", True):
            elems.remove(elem)


def dessiner_groupes(elems, ecran):
    for elem in elems:
        elem.dessiner(ecran)
