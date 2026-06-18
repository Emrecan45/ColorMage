import pygame
import core.temps as temps
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


cache_sons_pyrolord = {}

def charger_sons_pyrolord():
    """Charge les sons du Pyrolord."""
    if cache_sons_pyrolord:
        return cache_sons_pyrolord
    cache_sons_pyrolord["epee"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_epee.wav")))
    cache_sons_pyrolord["marche"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_marche.wav")))
    cache_sons_pyrolord["souffle"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_souffle_feu.wav")))
    cache_sons_pyrolord["degat"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "hurt.wav")))
    cache_sons_pyrolord["transfo"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_transformation.wav")))
    cache_sons_pyrolord["mort"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_mort.wav")))
    cache_sons_pyrolord["tire"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_tire.wav")))
    cache_sons_pyrolord["saut"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_saut.wav")))
    cache_sons_pyrolord["atter"] = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "pyrolord_atterissage.wav")))
    return cache_sons_pyrolord


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

    ECHELLE = 1.7 # échelle de la forme slime
    ECHELLE_BOSS = 1.5 # échelle de la forme boss
    CW, CH = 288, 160
    PV_DEFAUT = 10
    ENRAGE_SCALE = 1.18 # grossissement à l'enrage

    SWORD_S0, SWORD_S1 = 8, 13 # épée sortie
    SWORD_SON = 6 # déclenchement du son épée
    FIRE_S0, FIRE_S1 = 6, 16 # jet de feu
    LEAP_A0, LEAP_A1 = 5, 9 # phase aérienne du saut
    LEAP_SON = 4 # déclenchement du son de saut
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
        charger_assets_pyrolord(Pyrolord.ECHELLE_BOSS)
        charger_assets_pyrolord(Pyrolord.ECHELLE_BOSS * Pyrolord.ENRAGE_SCALE)
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
        self.last_anim = temps.obtenir_temps()

        # position et physique
        self.base_y = self.y
        self.hop_offset = 0.0
        self.leap_vx = 0.0
        self.leap_vx_vers_cible = 0.0
        self.walk_speed = 2.3
        self.walk_start = 0
        self.slime_hop_speed = 1.8

        # combat
        self.action_timer = temps.obtenir_temps()
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

        # sons
        sons = charger_sons_pyrolord()
        self.son_epee = sons["epee"]
        self.son_marche = sons["marche"]
        self.son_souffle = sons["souffle"]
        self.son_degat = sons["degat"]
        self.son_transfo = sons["transfo"]
        self.son_mort = sons["mort"]
        self.son_tire = sons["tire"]
        self.son_saut = sons["saut"]
        self.son_atter = sons["atter"]

        # couper la musique quand le slime est frappé
        self.event_couper_musique = False
        # instant de départ de la transformation
        self.transfo_start = 0

    def consommer_event_couper_musique(self):
        """Retourne True quand le slime vient d'être frappé."""
        if self.event_couper_musique:
            self.event_couper_musique = False
            return True
        return False

    def doit_jouer_musique_boss(self):
        """Vrai quand la musique de boss doit tourner (après la transformation du slime)."""
        return self.barre_visible()

    def maj_volume_sons(self, volume):
        """Applique le volume des effets aux sons du boss."""
        self.son_epee.set_volume(volume)
        self.son_marche.set_volume(volume)
        self.son_souffle.set_volume(volume)
        self.son_degat.set_volume(volume)
        self.son_transfo.set_volume(volume)
        self.son_mort.set_volume(volume)
        self.son_tire.set_volume(volume)
        self.son_saut.set_volume(volume)
        self.son_atter.set_volume(volume)

    def arreter_sons(self):
        """Coupe tous les sons du boss (pause, mort, changement de niveau)."""
        self.son_epee.stop()
        self.son_marche.stop()
        self.son_souffle.stop()
        self.son_transfo.stop()
        self.son_mort.stop()
        self.son_tire.stop()
        self.son_saut.stop()
        self.son_atter.stop()

    def appliquer_echelle(self, echelle):
        """Charge les masques/bboxes/dimensions pour l'échelle donnée."""
        a = charger_assets_pyrolord(echelle)
        self.echelle = echelle
        self.box_w = a["box_w"]
        self.box_h = a["box_h"]
        self.masks = a["masks"]
        self.bboxes = a["bboxes"]
        self.feet_bottom = a["feet_bottom"]

    def appliquer_echelle_repositionnee(self, echelle):
        """Change l'échelle en gardant les pieds au sol et le centre horizontal."""
        sol = self.base_y + self.feet_bottom
        cx = self.centre_corps()[0]
        self.appliquer_echelle(echelle)
        self.x = cx - self.box_w * 0.5
        self.base_y = sol - self.feet_bottom
        self.y = self.base_y - self.hop_offset
        self.maj_hitbox()

    def grandir(self, facteur):
        """Grossissement (enrage)."""
        self.appliquer_echelle_repositionnee(Pyrolord.ECHELLE_BOSS * facteur)


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
        """Collision entre un rectangle (ex: projectile) et le contour courant."""
        if rect.width <= 0 or rect.height <= 0:
            return False
        m = self.masque_courant()
        solide = pygame.mask.Mask((rect.width, rect.height), fill=True)
        return m.overlap(solide, (int(rect.x - self.x), int(rect.y - self.y))) is not None

    def touche_par_masque(self, autre_mask, pos):
        """Collision entre un masque (ex: joueur) placé en `pos` et le contour courant."""
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
        etait_slime = self.est_slime()
        if self.state == "walk" and etat != "walk":
            self.son_marche.stop()
        self.state = etat
        self.frame_index = 0
        self.last_anim = now
        self.a_tire = False
        if etat == "bounce":
            self.action_timer = now
        elif etat == "slime_hurt":
            # le slime est frappé, on coupe la musique de boss
            self.event_couper_musique = True
        elif etat == "walk":
            self.walk_start = now
            self.son_marche.play()
        elif etat == "fire":
            self.son_souffle.play()
        elif etat == "transform":
            self.son_transfo.play()
            self.transfo_start = now
        elif etat == "dying":
            self.son_mort.play()
        elif etat == "leap":
            self.leap_vx = self.leap_vx_vers_cible
        if etat != "leap":
            self.hop_offset = 0.0
        # passage de la forme slime à la forme boss
        if etait_slime and not self.est_slime():
            self.appliquer_echelle_repositionnee(Pyrolord.ECHELLE_BOSS)

    def stomp(self):
        """Le joueur saute sur / tire sur le slime : déclenche dégâts puis transformation."""
        if self.state == "slime":
            self.entrer("slime_hurt", temps.obtenir_temps())
            return True
        return False

    def encaisser(self, degats=1):
        """Inflige des dégâts au boss. Retourne True si la mort est déclenchée."""
        if not self.peut_etre_blesse() or self.state == "dying":
            return False
        now = temps.obtenir_temps()
        if now - self.dernier_degat < self.degat_cooldown:
            return False
        # coup encaissé
        self.dernier_degat = now
        self.flash_time = now
        self.flash_couleur = (255, 200, 120, 150)
        self.son_degat.play()
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


    def update(self, joueur, passif=False):
        """Met à jour le boss. Retourne la liste des nouveaux projectiles..
        passif = True quand le joueur est mort (le boss finit son animation en cours mais ne bouge plus et ne lance plus d'actions).
        """
        now = temps.obtenir_temps()
        nouveaux = []
        # En passif la marche bascule en pose neutre
        if passif and self.state == "walk":
            self.entrer("bounce", now)
        delay = self.delais[self.state]

        if self.state == "slime":
            if not passif:
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
            if not passif:
                self.regarder_joueur(joueur)
            if now - self.last_anim >= delay:
                self.last_anim = now
                self.frame_index = (self.frame_index + 1) % len(self.frames["bounce"])
            if not passif:
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
                if self.frame_index == Pyrolord.SWORD_SON:
                    self.son_epee.play()
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
                    self.son_tire.play()
                    nouveaux = self.tirer(joueur)
                if self.frame_index >= len(self.frames["proj"]):
                    self.entrer("bounce", now)

        elif self.state == "leap":
            if not passif and Pyrolord.LEAP_A0 <= self.frame_index <= Pyrolord.LEAP_A1:
                self.x += self.leap_vx
                self.borner_x()
            d = delay
            if self.frame_index < Pyrolord.LEAP_A0:
                d = int(delay * Pyrolord.LEAP_WINDUP_MULT)
            if now - self.last_anim >= d:
                self.last_anim = now
                self.frame_index += 1
                if self.frame_index == Pyrolord.LEAP_SON:
                    self.son_saut.play()
                if self.frame_index == Pyrolord.LEAP_A1 + 1:
                    self.son_atter.play()
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
                temps.obtenir_temps() - self.flash_time < self.flash_duree):
            surf = surf.copy()
            masque = pygame.mask.from_surface(surf)
            halo = masque.to_surface(setcolor=self.flash_couleur, unsetcolor=(0, 0, 0, 0))
            surf.blit(halo, (0, 0))
        dx = (self.box_w - surf.get_width()) * 0.5
        dy = (self.box_h - surf.get_height())
        ecran.blit(surf, (int(self.x + dx), int(self.y + dy)))

