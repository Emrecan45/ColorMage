import pygame
import os
import math
import random

from core.config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT, LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import charger_image


cache_projectile = {}


import math
from core.config import TAILLE_CELLULE
from entities.boss.boss import Boss
from entities.projectiles import ProjectilePyro

cache_assets_pyro = {}


cache_frames_natives_pyro = {}

def charger_frames_natives_pyrolord():
    if "frames" in cache_frames_natives_pyro:
        return cache_frames_natives_pyro["frames"]
    sheet = pygame.image.load(resource_path(os.path.join("assets/img/entities", "pyrolord.png"))).convert_alpha()
    cw = Pyrolord.CW
    ch = Pyrolord.CH
    frames = {}
    for state, segs in Pyrolord.SPEC.items():
        fl = []
        for (row, count) in segs:
            for c in range(count):
                fl.append(sheet.subsurface(pygame.Rect(c * cw, row * ch, cw, ch)).copy())
        frames[state] = fl
    cache_frames_natives_pyro["frames"] = frames
    return frames


def charger_assets_pyrolord(echelle):
    """Masques + bboxes du Pyrolord pour une échelle donnée, mis en cache."""
    key = round(echelle, 4)
    if key in cache_assets_pyro:
        return cache_assets_pyro[key]
    frames = charger_frames_natives_pyrolord()
    box_w = int(Pyrolord.CW * echelle)
    box_h = int(Pyrolord.CH * echelle)
    masks = {}
    bboxes = {}
    for state, fl in frames.items():
        ml = []
        bl = []
        for native in fl:
            scaled = pygame.transform.scale(native, (box_w, box_h))
            flipped = pygame.transform.flip(scaled, True, False)
            ml.append((pygame.mask.from_surface(scaled), pygame.mask.from_surface(flipped)))
            bl.append((scaled.get_bounding_rect(), flipped.get_bounding_rect()))
        masks[state] = ml
        bboxes[state] = bl
    # ligne des pieds
    grounded = ("slime", "slime_hurt", "bounce", "walk", "sword", "fire", "proj", "hurt")
    fb = 0
    for st in grounded:
        for (b0, b1) in bboxes[st]:
            if b0.h > 0:
                fb = max(fb, b0.bottom)
    if fb == 0:
        fb = box_h
    a = dict(box_w=box_w, box_h=box_h, masks=masks, bboxes=bboxes, feet_bottom=fb)
    cache_assets_pyro[key] = a
    return a


class Pyrolord(Boss):
    """Boss du feu : apparaît en slime, se transforme puis enchaîne ses attaques."""

    ECHELLE = 1.7
    CW, CH = 288, 160
    PV_DEFAUT = 12
    ENRAGE_SCALE = 1.18 # grossissement à l'enrage

    SWORD_S0, SWORD_S1 = 8, 13 # épée sortie
    FIRE_S0, FIRE_S1 = 6, 16 # jet de feu
    LEAP_A0, LEAP_A1 = 5, 9 # phase aérienne du saut
    LEAP_HIT0, LEAP_HIT1 = 7, 11 # frames létales du saut
    LEAP_WINDUP_MULT = 2.4 # ralentit l'élan pour prevenir l'esquive
    LEAP_MAX_DIST = 250 # distance horizontale max d'un bond
    PROJ_RELEASE = 3 # frame de lâcher du projectile
    SLIME_AIR0, SLIME_AIR1 = 8, 11 # frames aériennes du slime

    SPEC = {
        "slime": [(0, 6), (1, 8)],
        "slime_hurt": [(2, 6)],
        "transform": [(3, 32)],
        "bounce": [(4, 6)],
        "walk": [(5, 12)],
        "sword": [(6, 15)],
        "leap": [(7, 18)],
        "fire": [(8, 21)],
        "proj": [(9, 6)],
        "hurt": [(10, 5)],
        "dying": [(11, 20)],
    }

    def __init__(self, x, y, hp=None):
        if hp:
            pv = int(hp)
        else:
            pv = Pyrolord.PV_DEFAUT
        super().__init__(nom="PYROLORD", pv=pv,
                         enrage_seuil=0.5, enrage_scale=Pyrolord.ENRAGE_SCALE)

        self.frames = charger_frames_natives_pyrolord()
        self.echelle = Pyrolord.ECHELLE
        charger_assets_pyrolord(Pyrolord.ECHELLE * Pyrolord.ENRAGE_SCALE)
        self.appliquer_echelle(self.echelle)

        self.x = float(x)
        self.y = float(y)
        self.direction = -1

        self.delais = {
            "slime": 160, "slime_hurt": 140, "transform": 105, "bounce": 230,
            "walk": 130, "sword": 100, "leap": 95, "fire": 95, "proj": 160,
            "hurt": 140, "dying": 130,
        }

        self.state = "slime"
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()

        # position et physique
        self.base_y = self.y
        self.hop_offset = 0.0
        self.leap_vx = 0.0
        self.leap_vx_vers_cible = 0.0
        self.walk_speed = 2.3
        self.walk_start = 0
        self.slime_hop_speed = 1.8

        # combat
        self.action_timer = pygame.time.get_ticks()
        self.last_hit = 0
        self.hurt_cooldown = 550
        self.a_tire = False
        self.derniere_attaque_type = ModuleNotFoundError

        # rendu
        self.flash_time = 0
        self.flash_duree = 110
        self.flash_couleur = (255, 200, 120, 150)

        self.hitbox = pygame.Rect(0, 0, 1, 1)
        self.maj_hitbox()

    def appliquer_echelle(self, echelle):
        """Charge les masques/bboxes/dimensions pour l'échelle donnée."""
        a = charger_assets_pyrolord(echelle)
        self.echelle = echelle
        self.box_w = a["box_w"]
        self.box_h = a["box_h"]
        self.masks = a["masks"]
        self.bboxes = a["bboxes"]
        self.feet_bottom = a["feet_bottom"]

    def grandir(self, facteur):
        """Grossissement (enrage) : garde les pieds au sol et le centre horizontal."""
        sol = self.base_y + self.feet_bottom          # ligne de sol courante
        cx = self.centre_corps()[0]                   # centre horizontal courant
        self.appliquer_echelle(Pyrolord.ECHELLE * facteur)
        self.x = cx - self.box_w * 0.5
        self.base_y = sol - self.feet_bottom
        self.y = self.base_y - self.hop_offset
        self.maj_hitbox()


    def est_slime(self):
        return self.state in ("slime", "slime_hurt")

    def barre_visible(self):
        return self.state not in ("slime", "slime_hurt", "transform")

    def peut_etre_blesse(self):
        return self.alive and self.state in ("bounce", "walk", "sword", "leap", "fire", "proj", "hurt")

    def attaque_active(self):
        """Vrai si la frame courante d'une attaque doit tuer le joueur au contact."""
        if not self.alive:
            return False
        if self.state == "sword":
            return Pyrolord.SWORD_S0 <= self.frame_index <= Pyrolord.SWORD_S1
        if self.state == "fire":
            return Pyrolord.FIRE_S0 <= self.frame_index <= Pyrolord.FIRE_S1
        if self.state == "leap":
            return Pyrolord.LEAP_HIT0 <= self.frame_index <= Pyrolord.LEAP_HIT1
        return False

    def centre_corps(self):
        return (self.x + self.box_w * 0.5, self.y + self.box_h * 0.5)

    def index_direction(self):
        # 1 = regarde à droite, 0 = regarde à gauche
        if self.direction == 1:
            return 1
        else:
            return 0

    def masque_courant(self):
        arr = self.masks.get(self.state, self.masks["bounce"])
        return arr[min(self.frame_index, len(arr) - 1)][self.index_direction()]

    def maj_hitbox(self):
        arr = self.bboxes.get(self.state, self.bboxes["bounce"])
        b = arr[min(self.frame_index, len(arr) - 1)][self.index_direction()]
        if b.w == 0 or b.h == 0:
            self.hitbox.update(int(self.x), int(self.y), 0, 0)
        else:
            self.hitbox.update(int(self.x) + b.x, int(self.y) + b.y, b.w, b.h)

    def touche_par_rect(self, rect):
        """Collision pixel-précise entre un rectangle (ex: projectile) et le contour courant."""
        if rect.width <= 0 or rect.height <= 0:
            return False
        m = self.masque_courant()
        solide = pygame.mask.Mask((rect.width, rect.height), fill=True)
        return m.overlap(solide, (int(rect.x - self.x), int(rect.y - self.y))) is not None

    def touche_par_masque(self, autre_mask, pos):
        """Collision pixel-précise entre un masque (ex: joueur) placé en `pos` et le contour courant."""
        if autre_mask is None:
            return False
        m = self.masque_courant()
        return m.overlap(autre_mask, (int(pos[0] - self.x), int(pos[1] - self.y))) is not None

    def borner_x(self):
        min_x = 10 - 0.30 * self.box_w
        max_x = (LARGEUR_ECRAN - 10) - 0.70 * self.box_w
        if self.x < min_x:
            self.x = min_x
        elif self.x > max_x:
            self.x = max_x

    def entrer(self, etat, now):
        self.state = etat
        self.frame_index = 0
        self.last_anim = now
        self.a_tire = False
        if etat == "bounce":
            self.action_timer = now
        elif etat == "walk":
            self.walk_start = now
        elif etat == "leap":
            self.leap_vx = self.leap_vx_vers_cible
        if etat != "leap":
            self.hop_offset = 0.0

    def stomp(self):
        """Le joueur saute sur / tire sur le slime : déclenche dégâts puis transformation."""
        if self.state == "slime":
            self.entrer("slime_hurt", pygame.time.get_ticks())
            return True
        return False

    def encaisser(self, degats=1):
        """Inflige des dégâts au boss. Retourne True si la mort est déclenchée."""
        if not self.peut_etre_blesse() or self.state == "dying":
            return False
        now = pygame.time.get_ticks()
        if now - self.dernier_degat < self.degat_cooldown:
            return False
        # coup encaissé
        self.dernier_degat = now
        self.flash_time = now
        self.flash_couleur = (255, 200, 120, 150)
        # la classe Boss gère les PV et déclenche l'enrage
        if self.appliquer_degats(degats):
            self.entrer("dying", now)
            return True
        if self.state in ("bounce", "walk") and now - self.last_hit >= self.hurt_cooldown:
            self.last_hit = now
            self.entrer("hurt", now)
        return False

    def dist_joueur(self, joueur):
        if joueur is None:
            return 0.0
        jcx = joueur.x + joueur.largeur * 0.5
        return abs(jcx - self.centre_corps()[0])

    def regarder_joueur(self, joueur):
        if joueur is None:
            return
        jcx = joueur.x + joueur.largeur * 0.5
        jcy = joueur.y + joueur.hauteur * 0.5
        bcx, bcy = self.centre_corps()
        dx = abs(jcx - bcx)
        dy = bcy - jcy

        if dy > 40 and dx < 60:
            return
        if jcx >= bcx:
            self.direction = 1
        else:
            self.direction = -1

    ATTAQUES = ("sword", "leap", "fire", "proj")

    def choisir_sans_repeat(self, opts):
        """Choisit dans opts en évitant de refaire la même attaque deux fois de suite."""
        if not opts:
            return "proj"
        if self.derniere_attaque_type in opts and len(set(opts)) > 1:
            filtres = []
            for o in opts:
                if o != self.derniere_attaque_type:
                    filtres.append(o)
            if filtres:
                opts = filtres
        choix = random.choice(opts)
        if choix in Pyrolord.ATTAQUES:
            self.derniere_attaque_type = choix
        return choix

    def choisir_action(self, dist):
        opts = []
        if dist <= 250:
            opts += ["sword", "sword", "fire"]
        if 150 <= dist <= 780:
            opts += ["leap", "leap", "leap"]
        if 150 <= dist <= 780:
            opts += ["fire", "fire"]
        if dist > 250:
            opts += ["proj", "proj"]
        if dist > 430:
            opts += ["walk", "walk"]
        return self.choisir_sans_repeat(opts)

    def choisir_attaque(self, dist):
        opts = []
        if dist <= 250:
            opts += ["sword", "sword", "fire"]
        if 150 <= dist <= 780:
            opts += ["leap", "leap", "leap"]
        if 150 <= dist <= 780:
            opts += ["fire", "fire"]
        if dist > 250:
            opts += ["proj", "proj"]
        return self.choisir_sans_repeat(opts)


    def update(self, joueur):
        """Met à jour le boss. Retourne la liste des nouveaux projectiles."""
        now = pygame.time.get_ticks()
        nouveaux = []
        delay = self.delais[self.state]

        if self.state == "slime":
            self.regarder_joueur(joueur)
            if Pyrolord.SLIME_AIR0 <= self.frame_index <= Pyrolord.SLIME_AIR1:
                self.x += self.slime_hop_speed * self.direction
                self.borner_x()
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index = (self.frame_index + 1) % len(self.frames["slime"])

        elif self.state == "slime_hurt":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["slime_hurt"]):
                    self.entrer("transform", now)

        elif self.state == "transform":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["transform"]):
                    self.entrer("bounce", now)

        elif self.state == "bounce":
            self.regarder_joueur(joueur)
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index = (self.frame_index + 1) % len(self.frames["bounce"])
            if self.en_phase2:
                idle_time = 240
            else:
                idle_time = 420
            if now - self.action_timer >= idle_time:
                act = self.choisir_action(self.dist_joueur(joueur))
                self.regarder_joueur(joueur)
                if act == "leap":
                    self.preparer_leap(joueur)
                self.entrer(act, now)

        elif self.state == "walk":
            self.regarder_joueur(joueur)
            self.x += self.walk_speed * self.direction
            self.borner_x()
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index = (self.frame_index + 1) % len(self.frames["walk"])
            dist = self.dist_joueur(joueur)
            if dist <= 200 or now - self.walk_start >= 1100:
                act = self.choisir_attaque(dist)
                self.regarder_joueur(joueur)
                if act == "leap":
                    self.preparer_leap(joueur)
                self.entrer(act, now)

        elif self.state == "sword":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["sword"]):
                    self.entrer("bounce", now)

        elif self.state == "fire":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["fire"]):
                    self.entrer("bounce", now)

        elif self.state == "proj":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index == Pyrolord.PROJ_RELEASE and not self.a_tire:
                    self.a_tire = True
                    nouveaux = self.tirer(joueur)
                if self.frame_index >= len(self.frames["proj"]):
                    self.entrer("bounce", now)

        elif self.state == "leap":
            if Pyrolord.LEAP_A0 <= self.frame_index <= Pyrolord.LEAP_A1:
                self.x += self.leap_vx
                self.borner_x()
            d = delay
            if self.frame_index < Pyrolord.LEAP_A0:
                d = int(delay * Pyrolord.LEAP_WINDUP_MULT)
            if now - self.last_anim >= d:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["leap"]):
                    self.entrer("bounce", now)

        elif self.state == "hurt":
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["hurt"]):
                    self.entrer("bounce", now)

        elif self.state == "dying":
            self.hop_offset = 0.0
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index >= len(self.frames["dying"]):
                    self.frame_index = len(self.frames["dying"]) - 1
                    self.alive = False
                    self.finished = True

        self.y = self.base_y - self.hop_offset
        self.maj_hitbox()
        return nouveaux

    def preparer_leap(self, joueur):
        frames_anim = max(1, Pyrolord.LEAP_A1 - Pyrolord.LEAP_A0 + 1)
        duree_ms = frames_anim * self.delais["leap"]
        gameframes = max(1.0, duree_ms / (1000.0 / 60.0))
        if joueur is not None:
            dx = (joueur.x + joueur.largeur * 0.5) - self.centre_corps()[0]
        else:
            dx = 0.0
        dx = max(-Pyrolord.LEAP_MAX_DIST, min(Pyrolord.LEAP_MAX_DIST, dx))
        self.leap_vx_vers_cible = max(-35.0, min(35.0, dx / gameframes))

    def tirer(self, joueur):
        if self.direction == 1:
            mx = self.hitbox.right
        else:
            mx = self.hitbox.left
        my = self.hitbox.top + self.hitbox.height * 0.4
        vy = 0.0
        if joueur is not None:
            jcx = joueur.x + joueur.largeur * 0.5
            jcy = joueur.y + joueur.hauteur * 0.5
            dx = jcx - mx
            dy = jcy - my
            dist = max(1.0, math.hypot(dx, dy))
            vy = max(-3.5, min(3.5, dy / dist * 7.0))
        projs = []
        if self.en_phase2:
            for dv in (-2.6, 0.0, 2.6):
                projs.append(ProjectilePyro(mx, my, direction=self.direction, speed=4.5, vy=vy + dv))
        else:
            projs.append(ProjectilePyro(mx, my, direction=self.direction, speed=4.5, vy=vy))
        return projs

    def surface_affichee(self):
        frames = self.frames.get(self.state, self.frames["bounce"])
        idx = min(self.frame_index, len(frames) - 1)
        w = max(1, int(self.box_w * self.render_scale))
        h = max(1, int(self.box_h * self.render_scale))
        surf = pygame.transform.scale(frames[idx], (w, h))
        if self.direction == 1:
            surf = pygame.transform.flip(surf, True, False)
        return surf

    def dessiner(self, ecran):
        surf = self.surface_affichee()
        if (self.flash_time and self.state != "dying" and
                pygame.time.get_ticks() - self.flash_time < self.flash_duree):
            surf = surf.copy()
            masque = pygame.mask.from_surface(surf)
            halo = masque.to_surface(setcolor=self.flash_couleur, unsetcolor=(0, 0, 0, 0))
            surf.blit(halo, (0, 0))
        dx = (self.box_w - surf.get_width()) * 0.5
        dy = (self.box_h - surf.get_height())
        ecran.blit(surf, (int(self.x + dx), int(self.y + dy)))

