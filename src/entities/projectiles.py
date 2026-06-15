import pygame
import core.temps as temps
import os

from core.config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT, LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import charger_image


cache_projectile = {}


from core.config import TAILLE_CELLULE

def construire_assets_projectile(size):
    """Construit et met en cache les frames et masques pour une taille donnée."""
    if size in cache_projectile:
        return cache_projectile[size]
    sprite_w = 192
    sprite_h = 192
    sheet = charger_image(resource_path(os.path.join("assets/img/entities", "ennemy.png")), "alpha")
    frames = []
    collision_boxes = []
    masks = []
    for col in (0, 1, 2):
        sprite = sheet.subsurface(pygame.Rect(col * sprite_w, 1 * sprite_h, sprite_w, sprite_h))
        sprite = pygame.transform.scale(sprite, (size, size))
        mask = pygame.mask.from_surface(sprite)
        flipped_mask = pygame.mask.from_surface(pygame.transform.flip(sprite, True, False))
        box = mask.get_rect()
        if box.w == 0 or box.h == 0:
            box = pygame.Rect(0, 0, size, size)
        frames.append(sprite)
        collision_boxes.append(box)
        masks.append((mask, flipped_mask))
    explosion_frames = []
    for col in (0, 2):
        ex_sprite = sheet.subsurface(pygame.Rect(col * sprite_w, 2 * sprite_h, sprite_w, sprite_h))
        ex_sprite = pygame.transform.scale(ex_sprite, (size, size))
        explosion_frames.append(ex_sprite)
    cache = {"frames": frames, "collision_boxes": collision_boxes,
             "masks": masks, "explosion_frames": explosion_frames}
    cache_projectile[size] = cache
    return cache


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

        assets = construire_assets_projectile(self.size)
        self.frames = assets["frames"]
        self.collision_boxes = assets["collision_boxes"]
        self.masks = assets["masks"]
        self.explosion_frames = assets["explosion_frames"]

        self.cache_retournes = {}
        self.cache_explosion_retournes = {}

        self.frame_index = 0
        self.last_frame_time = temps.obtenir_temps()
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
        self.explosion_index = 0
        self.explosion_last_time = 0
        self.explosion_frame_delay = 120
        # max distance (None = infinite)
        self.max_distance = None

    def update(self):
        # animation
        now = temps.obtenir_temps()
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
            now = temps.obtenir_temps()
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
        self.explosion_last_time = temps.obtenir_temps()


# Frames du sorcier, construites une seule fois

cache_projectile_feu = {}


def construire_assets_feu():
    """Construit une seule fois les frames de création/traînée/explosion et leurs masques."""
    if "assets" in cache_projectile_feu:
        return cache_projectile_feu["assets"]
    size = 120
    sheet_c = charger_image(resource_path(os.path.join("assets/img/entities", "feu_creation.png")), "alpha")
    creation_frames = []
    for i in range(min(10, sheet_c.get_height() // 64)):
        frame = sheet_c.subsurface(pygame.Rect(0, i * 64, 64, 64))
        creation_frames.append(pygame.transform.scale(frame, (size, size)))

    sheet_t = charger_image(resource_path(os.path.join("assets/img/entities", "feu_trainee.png")), "alpha")
    trail_frames = []
    for i in range(sheet_t.get_height() // 64):
        frame = sheet_t.subsurface(pygame.Rect(0, i * 64, 64, 64))
        trail_frames.append(pygame.transform.scale(frame, (size, size)))
    trail_masks = []
    for s in trail_frames:
        trail_masks.append(pygame.mask.from_surface(s))

    sheet_e = charger_image(resource_path(os.path.join("assets/img/entities", "feu_explosion.png")), "alpha")
    explosion_frames = []
    for i in range(sheet_e.get_width() // 64):
        frame = sheet_e.subsurface(pygame.Rect(i * 64, 0, 64, 64))
        explosion_frames.append(pygame.transform.scale(frame, (size, size)))

    cache_projectile_feu["assets"] = {"creation_frames": creation_frames, "trail_frames": trail_frames,
                                      "trail_masks": trail_masks, "explosion_frames": explosion_frames}
    return cache_projectile_feu["assets"]


class ProjectileFeu:
    """Projectile de feu tiré par le mage."""
    size = 120  # taille d'affichage

    def __init__(self, x, y, direction=1, speed=VITESSE_DEPLACEMENT):
        self.direction = direction
        self.speed = speed
        self.alive = True
        self.collidable = False  # pas de collision pendant la création

        self.hit_w = 4  # très petite largeur pour être précis au centre
        self.hit_h = 2   # très plat pour passer facilement sous les blocs

        # centre du projectile
        self.centre_x = float(x)
        self.centre_y = float(y)
        self.x = self.centre_x - self.size // 2
        self.y = self.centre_y - self.size // 2

        self.rect = pygame.Rect(self.centre_x - self.hit_w / 2, self.centre_y - self.hit_h / 2, self.hit_w, self.hit_h)

        # Frames/masques partagés (construits une seule fois)
        a = construire_assets_feu()
        self.creation_frames = a["creation_frames"]
        self.trail_frames = a["trail_frames"]
        self.trail_masks = a["trail_masks"]
        self.explosion_frames = a["explosion_frames"]
        self.cache_trail_retourne = {}

        # États : "creation", "trail", "explosion"
        self.state = "creation"
        self.frame_index = 0
        self.last_frame_time = temps.obtenir_temps()
        self.creation_delay = 30
        self.trail_delay = 80
        self.explosion_delay = 60

        self.cache_retourne = {}
        self.cache_masques = {}

    def update(self):
        now = temps.obtenir_temps()

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
        
        # Calculer le centre visuel
        draw_y = self.y
        if self.state == "creation":
            draw_y += self.size // 2
        else:
            draw_y += 37
            
        visual_center_y = draw_y + self.size // 2
        
        self.rect.topleft = (int(self.centre_x - self.hit_w / 2), int(visual_center_y - self.hit_h / 2))

    def start_explosion(self):
        self.state = "explosion"
        self.frame_index = 0
        self.last_frame_time = temps.obtenir_temps()
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
        else:
            draw_y += 37
        ecran.blit(frame, (int(self.x), draw_y))

    def obtenir_masque_et_offset(self):
        """Retourne le masque pixel-perfect et sa position (x, y) de dessin."""
        frame = self.get_frame()
        if self.direction == -1:
            key = (self.state, self.frame_index)
            f = self.cache_retourne.get(key)
            if f is None:
                f = pygame.transform.flip(frame, True, False)
                self.cache_retourne[key] = f
            frame = f
        
        mask_key = ("mask", self.direction, self.state, self.frame_index)
        m = self.cache_masques.get(mask_key)
        if m is None:
            m = pygame.mask.from_surface(frame)
            self.cache_masques[mask_key] = m
            
        draw_y = int(self.y)
        if self.state == "creation":
            draw_y += self.size // 2
        else:
            draw_y += 37
        return m, (int(self.x), draw_y)


# Frames + masques du cristal, construits une seule fois


cache_pyro_projectile = {}

def charger_frames_pyro_projectile():
    if "frames" in cache_pyro_projectile:
        return cache_pyro_projectile["frames"]
    sheet = pygame.image.load(resource_path(os.path.join("assets/img/entities", "pyrolord_projectile.png"))).convert_alpha()
    fw, fh = 32, 32
    taille = 58

    def f(col, row):
        s = sheet.subsurface(pygame.Rect(col * fw, row * fh, fw, fh))
        return pygame.transform.scale(s, (taille, taille))

    travel = []
    for c in (0, 1, 2):
        travel.append(f(c, 0))
    explosion = []
    for c in range(10):
        explosion.append(f(c, 1))
    cache_pyro_projectile["frames"] = (travel, explosion, taille)
    return cache_pyro_projectile["frames"]


class ProjectilePyro:
    """Boule de feu tirée par le Pyrolord : vole vers le joueur puis explose."""

    def __init__(self, x, y, direction=1, speed=7.0, vy=0.0):
        self.travel_frames, self.explosion_frames, self.size = charger_frames_pyro_projectile()
        self.centre_x = float(x)
        self.centre_y = float(y)
        if direction >= 0:
            self.direction = 1
        else:
            self.direction = -1
        self.speed = float(speed)
        self.vy = float(vy)
        self.alive = True
        self.collidable = True
        self.state = "travel"
        self.frame_index = 0
        self.last_frame_time = temps.obtenir_temps()
        self.travel_delay = 80
        self.explosion_delay = 55
        self.hit_size = 34
        self.rect = pygame.Rect(0, 0, self.hit_size, self.hit_size)
        self.rect.center = (int(self.centre_x), int(self.centre_y))
        self.cache_flip = {}
        self.cache_masques = {}

    def update(self):
        now = temps.obtenir_temps()
        if self.state == "travel":
            self.centre_x += self.speed * self.direction
            self.centre_y += self.vy
            if now - self.last_frame_time >= self.travel_delay:
                self.last_frame_time = now
                self.frame_index = (self.frame_index + 1) % len(self.travel_frames)
            if (self.centre_x < -80 or self.centre_x > LARGEUR_ECRAN + 80 or
                    self.centre_y < -80 or self.centre_y > HAUTEUR_ECRAN + 120):
                self.alive = False
            self.rect.center = (int(self.centre_x), int(self.centre_y))
        else:  # explosion
            self.collidable = False
            if now - self.last_frame_time >= self.explosion_delay:
                self.last_frame_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.explosion_frames):
                    self.alive = False

    def start_explosion(self):
        if self.state != "explosion":
            self.state = "explosion"
            self.collidable = False
            self.frame_index = 0
            self.last_frame_time = temps.obtenir_temps()

    def frame_courante(self):
        if self.state == "travel":
            return self.travel_frames[self.frame_index % len(self.travel_frames)]
        idx = min(self.frame_index, len(self.explosion_frames) - 1)
        return self.explosion_frames[idx]

    def dessiner(self, ecran):
        frame = self.frame_courante()
        if self.direction == -1:
            key = (self.state, self.frame_index)
            fl = self.cache_flip.get(key)
            if fl is None:
                fl = pygame.transform.flip(frame, True, False)
                self.cache_flip[key] = fl
            frame = fl
        ecran.blit(frame, (int(self.centre_x - self.size / 2), int(self.centre_y - self.size / 2)))

    def obtenir_masque_et_offset(self):
        """Retourne le masque pixel-perfect et sa position (x, y) de dessin."""
        frame = self.frame_courante()
        if self.direction == -1:
            key = (self.state, self.frame_index)
            fl = self.cache_flip.get(key)
            if fl is None:
                fl = pygame.transform.flip(frame, True, False)
                self.cache_flip[key] = fl
            frame = fl
            
        mask_key = ("mask", self.direction, self.state, self.frame_index)
        m = self.cache_masques.get(mask_key)
        if m is None:
            m = pygame.mask.from_surface(frame)
            self.cache_masques[mask_key] = m
            
        return m, (int(self.centre_x - self.size / 2), int(self.centre_y - self.size / 2))


cache_frames_natives_pyro = {}

