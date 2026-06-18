import pygame
import core.temps as temps
import json
import random
import math
import os
from core.config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS, LARGEUR_ECRAN, HAUTEUR_ECRAN, resource_path
from entities import Sorcier
from entities import Squelette
from entities import Slime
from entities import Piece
from entities import CristalFeu
from entities import Pyrolord
from entities import Demon, DEMON_W, DEMON_H
from core.assets import charger_image, charger_son_accelere
from entities.obstacles import FeuBloc, PicBloc
from core.config_manager import ConfigManager
from entities import Piece, CristalFeu

class PlateformeMobile:
    """Plateforme qui bouge horizontalement ou verticallement."""
    def __init__(self, cell_x, cell_y, dirv=1, range_blocks=1, sens=1, speed_px=1.0):
        self.cell_x = int(cell_x)
        self.cell_y = int(cell_y)
        self.dir = int(dirv)  # 1 = horizontal, -1 = vertical
        # s'assurer que les valeurs sont positives
        try:
            if range_blocks is not None:
                self.range_blocks = abs(int(range_blocks))
            else:
                self.range_blocks = 1
        except Exception:
            self.range_blocks = 1
        try:
            if speed_px is not None:
                self.vitesse = abs(float(speed_px))
            else:
                self.vitesse = 1.0
        except Exception:
            self.vitesse = 1.0
        
        # position d'origine
        self.origine_x = self.cell_x * TAILLE_CELLULE
        self.origine_y = self.cell_y * TAILLE_CELLULE
        
        # plage de déplacement
        self.plage = self.range_blocks * TAILLE_CELLULE
        # 1 ou -1
        try:
            self.sens = int(sens)
            if self.sens not in (-1, 1):
                self.sens = 1
        except Exception:
            self.sens = 1

        self.decalage = 0
        self.sens_direction = 1
        
        # position courante en pixels
        if self.dir == 1:
            self.x = self.origine_x
            self.y = self.origine_y
        else:
            self.x = self.origine_x
            self.y = self.origine_y
        
        # pour transmettre le déplacement auxentités
        self.dernier_dx = 0
        self.dernier_dy = 0
        
        # taille de la plateforme (1 cellule)
        self.largeur = TAILLE_CELLULE
        self.hauteur = int(TAILLE_CELLULE // 2)
        
        # couleur (par defaut noir)
        self.couleur = "noir"

    def maj(self):
        """Met à jour la position et retourne (dx, dy)."""
        old_x = self.x
        old_y = self.y
        # avancer le décalage
        self.decalage += self.vitesse * self.sens_direction
        if self.decalage > self.plage:
            self.decalage = self.plage
            self.sens_direction = -1
        if self.decalage < 0:
            self.decalage = 0
            self.sens_direction = 1
        if self.dir == 1:
            # horizontal
            self.x = int(self.origine_x + self.sens * self.decalage)
            self.y = self.origine_y
        else:
            # vertical
            self.x = self.origine_x
            self.y = int(self.origine_y + self.sens * self.decalage)
        self.dernier_dx = int(self.x - old_x)
        self.dernier_dy = int(self.y - old_y)
        return (self.dernier_dx, self.dernier_dy)

    def obtenir_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur)

    def dessiner(self, ecran):
        draw_color = (30, 30, 30)
        if self.couleur in COULEURS:
            draw_color = COULEURS[self.couleur]
        elif self.couleur == 'noir':
            draw_color = (30, 30, 30)
        pygame.draw.rect(ecran, draw_color, (int(self.x), int(self.y), self.largeur, self.hauteur))


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self, gestionnaire_config=None):
        self.grille = []
        self.spawn_cell = None
        self.numero_niveau = 1
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        # entités du niveau
        self.sorciers = []
        self.squelettes = []
        self.projectiles = []
        self.slimes = []
        self.pieces = []
        # démons volants
        self.demons = []
        # plateformes mobiles
        self.platformes_mobiles = []
        # Projectiles du joueur et cristaux
        self.projectiles_joueur = []
        self.cristaux_feu = []
        self.positions_cristal_feu = []  # positions possibles pour les power ups
        self.dernier_collecte_cristal = 0
        # Boss
        self.boss = None
        self.projectiles_boss = []
        self.projectiles_demon = []
        self.porte_boss = None  # (x, y) porte de sortie à la mort du boss
        self.intervalle_spawn_cristal = 25000  # 25s entre chaque spawn possible
        self.traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic", "feu"]
        self.image_pic = pygame.transform.scale(charger_image(resource_path("assets/img/items/pic.png")), (TAILLE_CELLULE, TAILLE_CELLULE))
        # Feu
        sheet_feu = charger_image(resource_path("assets/img/items/feu.png"))
        nb_feu = 8
        fw_feu = sheet_feu.get_width() // nb_feu
        fh_feu = sheet_feu.get_height()
        self.feu_largeur = TAILLE_CELLULE
        self.feu_hauteur = TAILLE_CELLULE * 2
        self.frames_feu = []
        for i in range(nb_feu):
            fr = sheet_feu.subsurface(pygame.Rect(i * fw_feu, 0, fw_feu, fh_feu))
            self.frames_feu.append(pygame.transform.smoothscale(fr, (self.feu_largeur, self.feu_hauteur)))
        self.image_feu = self.frames_feu[0]
        meilleur_compte = pygame.mask.from_surface(self.image_feu).count()
        for frame in self.frames_feu:
            compte = pygame.mask.from_surface(frame).count()
            if compte > meilleur_compte:
                meilleur_compte = compte
                self.image_feu = frame
        sheet_fum = charger_image(resource_path("assets/img/items/fumee.png"))
        nb_fum = 8
        fw_fum = sheet_fum.get_width() // nb_fum
        fh_fum = sheet_fum.get_height()
        fum_w = int(TAILLE_CELLULE * 0.8)
        fum_h = int(TAILLE_CELLULE * 1.6)
        self.frames_fumee = []
        for i in range(nb_fum):
            fr = sheet_fum.subsurface(pygame.Rect(i * fw_fum, 0, fw_fum, fh_fum))
            fr = pygame.transform.smoothscale(fr, (fum_w, fum_h)).convert_alpha()
            fr.set_alpha(110)
            self.frames_fumee.append(fr)
        self.image_porte = pygame.transform.scale(charger_image(resource_path("assets/img/items/porte.png")), (TAILLE_CELLULE, TAILLE_CELLULE))
        # Images des potions (anciennement les portails de couleur)
        self.images_potion = {}
        img_r = charger_image(resource_path("assets/img/items/change_rouge.png"))
        img_b = charger_image(resource_path("assets/img/items/change_bleu.png"))
        img_v = charger_image(resource_path("assets/img/items/change_vert.png"))

        if img_r:
            self.images_potion['change_rouge'] = pygame.transform.smoothscale(img_r, (TAILLE_CELLULE, TAILLE_CELLULE))
        if img_b:
            self.images_potion['change_bleu'] = pygame.transform.smoothscale(img_b, (TAILLE_CELLULE, TAILLE_CELLULE))
        if img_v:
            self.images_potion['change_vert'] = pygame.transform.smoothscale(img_v, (TAILLE_CELLULE, TAILLE_CELLULE))
        # Masques pour collision
        self.masks_potion = {}
        for k, surf in self.images_potion.items():
            self.masks_potion[k] = pygame.mask.from_surface(surf)
        # Sons aléatoires pour le sorcier (tir) et le squelette (attaque)
        self.sons_sorcier_shot = []
        for i in range(1, 4):
            son = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "sorcier_shot" + str(i) + ".wav")))
            self.sons_sorcier_shot.append(son)
        self.sons_squelette_tape = []
        for i in range(1, 4):
            son = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "squelette_tape" + str(i) + ".ogg")))
            self.sons_squelette_tape.append(son)
        # Tir et charge des démons
        self.son_demon_tir = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "demon_tir.wav")))
        self.son_demon_fonce = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "demon_fonce.wav")))
        # Ambiances en boucle
        self.son_feu = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "feu.wav")))
        self.son_demon_vol = charger_son_accelere(resource_path(os.path.join("assets/audio", "demon_vol.wav")), 2.5)
        self.feu_en_cours = False
        self.demon_vol_en_cours = False
        self.maj_volume_sons()

        # stocker les infos des étoiles pour le fond
        self.etoiles_fond = []
        for i in range(100):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, int(HAUTEUR_ECRAN * 0.7))
            taille = random.randint(1, 2)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            phase = random.uniform(0, 2 * math.pi)
            self.etoiles_fond.append([x, y, taille, brillance, vitesse_scintillement, phase])
        self.dernier_tick_maj_plat = -1
        self.feux = []
        self.pics = []

    def obtenir_decalage_potion(self, cell_x, cell_y):
        """Bobbing vertical pour les potions"""
        amplitude = TAILLE_CELLULE * 0.12
        phase = (cell_x * 0.6) + (cell_y * 1.1) # ajouter un offset de phase pour avoir des potions qui bougent de manière décalée
        bob_f = amplitude * math.sin(temps.obtenir_temps() * 0.003 + phase)
        base_lift = int(TAILLE_CELLULE * 0.45)
        return base_lift, int(bob_f)
    
    def maj_volume_sons(self):
        """Met à jour le volume des sons d'ennemis"""
        volumes = self.gestionnaire_config.volumes
        vol_effets = volumes.get("effets", 50) / 100
        for son in self.sons_sorcier_shot:
            son.set_volume(vol_effets)
        for son in self.sons_squelette_tape:
            son.set_volume(vol_effets)
        self.son_demon_tir.set_volume(vol_effets)
        self.son_demon_fonce.set_volume(vol_effets)
        # l'ambiance de feu discrète
        self.son_feu.set_volume(vol_effets * 0.15)
        self.son_demon_vol.set_volume(vol_effets * 1.9)
        if self.boss is not None:
            self.boss.maj_volume_sons(vol_effets)

    def regler_ambiances(self, actif, feu_actif=None, demon_actif=None, boss_actif=None):
        """Démarre/arrête les boucles d'ambiance (feu, vol du démon) et coupe les
        sons du boss hors jeu."""
        if feu_actif is None:
            feu_actif = actif
        if demon_actif is None:
            demon_actif = actif
        if boss_actif is None:
            boss_actif = actif
        veut_feu = feu_actif and bool(self.feux)
        if veut_feu != self.feu_en_cours:
            if veut_feu:
                self.son_feu.play(-1)
            else:
                self.son_feu.stop()
            self.feu_en_cours = veut_feu

        veut_demon = demon_actif and any(not d.en_train_de_mourir for d in self.demons)
        if veut_demon != self.demon_vol_en_cours:
            if veut_demon:
                self.son_demon_vol.play(-1)
            else:
                self.son_demon_vol.stop()
            self.demon_vol_en_cours = veut_demon

        if not boss_actif and self.boss is not None:
            self.boss.arreter_sons()

    def creer_grille_vide(self):
        """Crée une grille vide"""
        self.grille = []
        for b in range(HAUTEUR_GRILLE):
            ligne = []
            for a in range(LARGEUR_GRILLE):
                ligne.append("vide")
            self.grille.append(ligne)
    
    def charger_depuis_json(self, numero):
        """Charge un niveau depuis un fichier JSON"""
        self.numero_niveau = numero
        planetes = ["terra", "pyros", "aquaris", "nebula", "cryon", "solara", "vortex", "obscura"]
        planete_idx = (numero - 1) // 5
        if planete_idx < len(planetes):
            planete = planetes[planete_idx]
        else:
            planete = "terra"
        chemin = resource_path(os.path.join("levels", planete, "niveau_" + str(numero) + ".json"))
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.creer_grille_vide()
        self.spawn_cell = None
        # couper les sons de l'ancien niveau avant de tout réinitialiser
        self.son_feu.stop()
        self.feu_en_cours = False
        self.son_demon_vol.stop()
        self.demon_vol_en_cours = False
        if self.boss is not None:
            self.boss.arreter_sons()
        # reset
        self.sorciers = []
        self.projectiles = []
        self.squelettes = []
        self.slimes = []
        self.pieces = []
        self.demons = []
        self.platformes_mobiles = []
        self.projectiles_joueur = []
        self.cristaux_feu = []
        self.positions_cristal_feu = []
        self.feux = []
        self.pics = []
        self.dernier_collecte_cristal = temps.obtenir_temps()
        self.boss = None
        self.projectiles_boss = []
        self.projectiles_demon = []
        self.porte_boss = None
        for type_bloc, positions in data.items():
            if type_bloc == "spawn":
                x, y = positions
                self.spawn_cell = (x, y)
                self.grille[y][x] = "vide"
            elif type_bloc == "sorcier":
                for item in positions:
                    item, drop = self.extraire_drop(item)
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue
                    dirv = 1
                    if len(item) >= 3:
                        dirv = int(item[2])
                    range_blocks = None
                    if len(item) >= 4:
                        range_blocks = int(item[3])
                    self.creer_sorcier(x, y, dirv, range_blocks, drop)
            elif type_bloc == "squelette":
                for item in positions:
                    item, drop = self.extraire_drop(item)
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue
                    dirv = 1
                    if len(item) >= 3:
                        dirv = int(item[2])
                    walk_blocks = 3
                    if len(item) >= 4:
                        walk_blocks = int(item[3])
                    self.creer_squelette(x, y, dirv, walk_blocks, drop)
            elif type_bloc == "slime_vert" or type_bloc == "slime_violet":
                if type_bloc == "slime_vert":
                    couleur_slime = "vert"
                else:
                    couleur_slime = "violet"
                for item in positions:
                    item, drop = self.extraire_drop(item)
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue
                    self.creer_slime(x, y, couleur_slime, drop)
            elif type_bloc == "demon":
                for item in positions:
                    item, drop = self.extraire_drop(item)
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue
                    self.creer_demon(x, y, drop)
            elif type_bloc == "feu":
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    nouveau_feu = FeuBloc(x, y, TAILLE_CELLULE)
                    self.feux.append(nouveau_feu)
                    self.grille[y][x] = "vide"
            elif type_bloc == "pic":
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    nouveau_pic = PicBloc(x, y, TAILLE_CELLULE)
                    self.pics.append(nouveau_pic)
                    self.grille[y][x] = "vide"
            elif type_bloc == "piece":
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    px = x * TAILLE_CELLULE
                    py = y * TAILLE_CELLULE
                    piece = Piece(px, py)
                    piece.cell_x = x
                    piece.cell_y = y
                    self.pieces.append(piece)
                    self.grille[y][x] = "vide"
            elif type_bloc.startswith("mobile_"):
                parts = type_bloc.split("_")
                if len(parts) >= 2:
                    couleur = parts[1]
                else:
                    continue
                # positions: [x, y, dir, range, sens, speed]
                for item in positions:
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue

                    dirv = 1
                    sens = 1
                    range_blocks = 1
                    speed_px = 1.0

                    try:
                        if len(item) >= 3:
                            dirv = int(item[2])

                        if len(item) >= 6:
                            a3 = int(item[3])
                            a4 = int(item[4])
                            # détecter le sens (-1 ou 1)
                            if a3 in (-1, 1) and a4 not in (-1, 1):
                                sens = a3
                                range_blocks = int(item[4])
                            elif a4 in (-1, 1) and a3 not in (-1, 1):
                                range_blocks = int(item[3])
                                sens = a4
                            else:
                                if a3 in (-1, 1):
                                    sens = a3
                                else:
                                    sens = 1
                                range_blocks = int(item[4])
                            speed_px = float(item[5])
                        elif len(item) == 5:
                            a3 = int(item[3])
                            a4 = int(item[4])
                            if a3 in (-1, 1) and a4 not in (-1, 1):
                                sens = a3
                                range_blocks = a4
                            elif a4 in (-1, 1) and a3 not in (-1, 1):
                                range_blocks = a3
                                sens = a4
                            else:
                                range_blocks = a3
                                if a4 in (-1, 1):
                                    sens = a4
                                else:
                                    sens = 1
                        elif len(item) == 4:
                            range_blocks = int(item[3])
                            sens = 1
                        elif len(item) == 3:
                            dirv = int(item[2])
                            sens = 1
                            range_blocks = 1
                    except Exception:
                        continue

                    plat = PlateformeMobile(x, y, dirv=dirv, range_blocks=range_blocks, sens=sens, speed_px=speed_px)
                    plat.couleur = couleur
                    self.platformes_mobiles.append(plat)
                    # ne pas laisser de bloc dans la grille (plateforme gérée séparément)
                    self.grille[y][x] = "vide"
            elif type_bloc == "cristal_feu":
                # Positions possibles pour les power-ups de feu
                for pos in positions:
                    px = pos[0] * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    py = pos[1] * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    self.positions_cristal_feu.append((px, py))
            elif type_bloc == "pyrolord":
                for item in positions:
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue
                    if len(item) >= 3:
                        hp = int(item[2])
                    else:
                        hp = None
                    boss = Pyrolord(0, 0, hp=hp)
                    sol = (y + 1) * TAILLE_CELLULE
                    boss.x = float(x * TAILLE_CELLULE + TAILLE_CELLULE // 2 - boss.box_w // 2)
                    boss.y = float(sol - boss.feet_bottom)
                    boss.base_y = boss.y
                    boss.maj_hitbox()
                    boss.maj_volume_sons(self.gestionnaire_config.volumes.get("effets", 50) / 100)
                    self.boss = boss
                    self.grille[y][x] = "vide"
            elif type_bloc == "porte_boss":
                try:
                    self.porte_boss = (int(positions[0]), int(positions[1]))
                except Exception:
                    self.porte_boss = None

            else:
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    self.grille[y][x] = type_bloc
        
        # Spawn un power-up de feu au début si des positions existent
        if self.positions_cristal_feu:
            pos = random.choice(self.positions_cristal_feu)
            cristal = CristalFeu(pos[0], pos[1])
            self.cristaux_feu.append(cristal)

        return self.grille

    def extraire_drop(self, item):
        """Sépare le drop optionnel (string en fin de liste) des arguments d'un monstre."""
        drop = None
        if type(item) == list and len(item) > 0 and type(item[-1]) == str:
            drop = item[-1]
            item = item[:-1]
        return item, drop

    def creer_sorcier(self, x, y, dirv=1, range_blocks=None, drop=None):
        """Crée et positionne un sorcier sur la grille."""
        px = x * TAILLE_CELLULE
        if dirv == 1:
            direction_val = 1
        else:
            direction_val = -1
        sorcier = Sorcier(px, 0, direction=direction_val, shoot_range_blocks=range_blocks)

        rect_w = sorcier.width - 2 * sorcier.marge_x
        cell_cx = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
        new_rect_left = cell_cx - rect_w // 2
        sorcier.x = int(new_rect_left - sorcier.marge_x)

        cell_top_px = y * TAILLE_CELLULE
        rect_h = sorcier.height - sorcier.marge_y_haut - sorcier.marge_y_bas
        rect_top = cell_top_px - rect_h
        sorcier.y = int(rect_top - sorcier.marge_y_haut + 53)

        sorcier.rect.topleft = (int(sorcier.x + sorcier.marge_x), int(sorcier.y + sorcier.marge_y_haut))
        sorcier.drop = drop
        sorcier.drop_fait = False
        self.sorciers.append(sorcier)
        # laisser la case vide pour ne pas bloquer le joueur
        if 0 <= y < HAUTEUR_GRILLE and 0 <= x < LARGEUR_GRILLE:
            self.grille[y][x] = "vide"
        return sorcier

    def creer_squelette(self, x, y, dirv=1, walk_blocks=3, drop=None):
        """Crée et positionne un squelette sur la grille."""
        px = x * TAILLE_CELLULE
        if dirv == 1:
            direction_val = 1
        else:
            direction_val = -1
        squelette = Squelette(px, 0, direction=direction_val, walk_blocks=walk_blocks)

        rect_w = squelette.width - 2 * squelette.marge_x
        cell_cx = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
        new_rect_left = cell_cx - rect_w // 2
        squelette.x = int(new_rect_left - squelette.marge_x)

        cell_top_px = y * TAILLE_CELLULE
        rect_h = squelette.height - squelette.marge_y_haut - squelette.marge_y_bas
        rect_top = cell_top_px - rect_h
        squelette.y = int(rect_top - squelette.marge_y_haut + 50)

        squelette.rect.topleft = (int(squelette.x + squelette.marge_x), int(squelette.y + squelette.marge_y_haut))
        squelette.origin_x = squelette.x
        squelette.drop = drop
        squelette.drop_fait = False
        self.squelettes.append(squelette)
        if 0 <= y < HAUTEUR_GRILLE and 0 <= x < LARGEUR_GRILLE:
            self.grille[y][x] = "vide"
        return squelette

    def creer_slime(self, x, y, couleur, drop=None):
        """Crée un slime sur la grille."""
        px = x * TAILLE_CELLULE
        py = y * TAILLE_CELLULE
        slime = Slime(px, py, couleur=couleur)
        slime.drop = drop
        slime.drop_fait = False
        self.slimes.append(slime)
        if 0 <= y < HAUTEUR_GRILLE and 0 <= x < LARGEUR_GRILLE:
            self.grille[y][x] = "vide"
        return slime

    def creer_demon(self, x, y, drop=None):
        """Crée un démon volant sur la grille."""
        px = x * TAILLE_CELLULE + TAILLE_CELLULE // 2 - DEMON_W // 2
        py = y * TAILLE_CELLULE + TAILLE_CELLULE // 2 - DEMON_H // 2
        demon = Demon(px, py)
        demon.drop = drop
        demon.drop_fait = False
        self.demons.append(demon)
        if 0 <= y < HAUTEUR_GRILLE and 0 <= x < LARGEUR_GRILLE:
            self.grille[y][x] = "vide"
        return demon

    def appliquer_drop(self, monstre):
        """Fait apparaître le drop d'un monstre à l'endroit de sa mort."""
        drop = monstre.drop
        if not drop:
            return
        if monstre.drop_fait:
            return
        monstre.drop_fait = True

        centre = monstre.rect.center
        cx_px = centre[0]
        cy_px = centre[1]
        cell_x = int(cx_px // TAILLE_CELLULE)
        cell_y = int(cy_px // TAILLE_CELLULE)

        dans_grille = (0 <= cell_y < HAUTEUR_GRILLE and 0 <= cell_x < LARGEUR_GRILLE)

        if drop == "piece":
            piece = Piece(cell_x * TAILLE_CELLULE, cell_y * TAILLE_CELLULE)
            piece.cell_x = cell_x
            piece.cell_y = cell_y
            self.pieces.append(piece)
        elif drop == "change_rouge" or drop == "change_bleu" or drop == "change_vert":
            if dans_grille:
                self.grille[cell_y][cell_x] = drop
        elif drop == "cristal_feu":
            cristal = CristalFeu(cx_px, cy_px)
            self.cristaux_feu.append(cristal)
        elif drop == "sorcier":
            self.creer_sorcier(cell_x, cell_y)
        elif drop == "squelette":
            self.creer_squelette(cell_x, cell_y)
        elif drop == "slime_vert":
            self.creer_slime(cell_x, cell_y, "vert")
        elif drop == "slime_violet":
            self.creer_slime(cell_x, cell_y, "violet")
        elif drop == "demon":
            self.creer_demon(cell_x, cell_y)

    def obtenir_spawn_pixel(self):
        """Retourne la position de spawn en pixels (x_px, y_px) ou None si absent."""
        if self.spawn_cell is None:
            return None
        x_cell, y_cell = self.spawn_cell
        x_px = x_cell * TAILLE_CELLULE
        y_px = y_cell * TAILLE_CELLULE - TAILLE_CELLULE # pour que le joueur soit au-dessus du sol
        return (x_px, y_px)
    
    def charger_niveau(self, numero, ecran):
        """Charge le niveau correspondant au numéro"""
        self.grille = self.charger_depuis_json(numero)

    def reset(self, numero, ecran):
        """Réinitialise le niveau"""
        self.charger_niveau(numero, ecran)
    
    def obtenir_bloc(self, x, y):
        """Retourne le type de bloc à une position donnée"""
        if 0 <= x < LARGEUR_GRILLE and 0 <= y < HAUTEUR_GRILLE:
            return self.grille[y][x]
        return "vide"
    
    def collision(self, rect, couleur_joueur):
        """Vérifie si un rectangle entre en collision avec un bloc solide"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                # Blocs toujours solides
                if bloc == "noir":
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
                
                # Blocs de couleur (solides seulement si même couleur)
                elif bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
        # plateformes
        for plat in self.platformes_mobiles:
            pr = plat.obtenir_rect()
            if plat.couleur is None or plat.couleur == "noir":
                if rect.colliderect(pr):
                    return True
            else:
                if plat.couleur in ["rouge", "bleu", "vert", "gris"] and plat.couleur == couleur_joueur:
                    if rect.colliderect(pr):
                        return True
        return False

    def tenter_spawn_cristal_feu(self):
        """Essaie de faire apparaître un cristal de feu si les conditions sont remplies."""
        if not self.positions_cristal_feu:
            return
        # Pas de spawn si un cristal est déjà présent
        if self.cristaux_feu:
            return
        now = temps.obtenir_temps()
        if now - self.dernier_collecte_cristal < self.intervalle_spawn_cristal:
            return
        pos = random.choice(self.positions_cristal_feu)
        cristal = CristalFeu(pos[0], pos[1])
        self.cristaux_feu.append(cristal)

    def forcer_spawn_cristal_feu(self):
        """Fait apparaître immédiatement un cristal de feu (ignorer le cooldown).
        Appelé quand le pouvoir de feu du joueur prend fin."""
        if not self.positions_cristal_feu:
            return
        # Pas de spawn si un cristal est déjà présent
        if self.cristaux_feu:
            return
        pos = random.choice(self.positions_cristal_feu)
        cristal = CristalFeu(pos[0], pos[1])
        self.cristaux_feu.append(cristal)
        self.dernier_collecte_cristal = temps.obtenir_temps()

    def collision_projectile_mur(self, projectile, couleur_joueur=None):
        """Le feu du joueur se casse sur un bloc noir ou de sa couleur (sinon il passe)."""
        if projectile.state != "trail":
            return False

        proj_mask, (px, py) = projectile.obtenir_masque_et_offset()
        proj_rect = pygame.Rect(px, py, projectile.size, projectile.size)
        bloc_mask = pygame.Mask((TAILLE_CELLULE, TAILLE_CELLULE), fill=True)

        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                bloque = False
                if bloc == "noir":
                    bloque = True
                elif couleur_joueur and bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloque = True
                if bloque:
                    bx = x * TAILLE_CELLULE
                    by = y * TAILLE_CELLULE
                    if bx + TAILLE_CELLULE < px or bx > px + projectile.size:
                        continue
                    if by + TAILLE_CELLULE < py or by > py + projectile.size:
                        continue
                    offset = (bx - px, by - py)
                    if proj_mask.overlap(bloc_mask, offset) is not None:
                        return True

        for plat in self.platformes_mobiles:
            pr = plat.obtenir_rect()
            if not proj_rect.colliderect(pr):
                continue
            bloque = False
            if plat.couleur is None or plat.couleur == "noir":
                bloque = True
            elif couleur_joueur and plat.couleur == couleur_joueur:
                bloque = True
            if bloque:
                p_mask = pygame.Mask((pr.width, pr.height), fill=True)
                offset = (pr.x - px, pr.y - py)
                if proj_mask.overlap(p_mask, offset) is not None:
                    return True
        return False

    def collision_projectile_boss(self, projectile, couleur_joueur=None):
        """Le projectile du boss se casse sur les blocs noirs et ceux de la couleur du mage. Il traverse les blocs des autres couleurs."""
        if projectile.state != "travel":
            return False

        proj_mask, (px, py) = projectile.obtenir_masque_et_offset()
        proj_rect = pygame.Rect(px, py, projectile.size, projectile.size)
        bloc_mask = pygame.Mask((TAILLE_CELLULE, TAILLE_CELLULE), fill=True)

        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                bloque = False
                if bloc == "noir":
                    bloque = True
                elif couleur_joueur and bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloque = True
                if bloque:
                    bx, by = x * TAILLE_CELLULE, y * TAILLE_CELLULE
                    if bx + TAILLE_CELLULE < px or bx > px + projectile.size or by + TAILLE_CELLULE < py or by > py + projectile.size:
                        continue
                    offset = (bx - px, by - py)
                    if proj_mask.overlap(bloc_mask, offset) is not None:
                        return True

        for plat in self.platformes_mobiles:
            pr = plat.obtenir_rect()
            if not proj_rect.colliderect(pr):
                continue
            bloque = False
            if plat.couleur is None or plat.couleur == "noir":
                bloque = True
            elif couleur_joueur and plat.couleur == couleur_joueur:
                bloque = True
            if bloque:
                p_mask = pygame.Mask((pr.width, pr.height), fill=True)
                offset = (pr.x - px, pr.y - py)
                if proj_mask.overlap(p_mask, offset) is not None:
                    return True
        return False

    def collision_projectile_demon(self, projectile, couleur_joueur=None):
        """Le projectile du démon se casse sur les blocs noirs, ceux de la couleur du mage et les plateformes."""
        proj_mask = projectile.masque_courant()
        px, py = projectile.offset_dessin()
        proj_rect = pygame.Rect(px, py, projectile.largeur, projectile.hauteur)
        bloc_mask = pygame.Mask((TAILLE_CELLULE, TAILLE_CELLULE), fill=True)

        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                bloque = False
                if bloc == "noir":
                    bloque = True
                elif couleur_joueur and bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloque = True
                if bloque:
                    bx = x * TAILLE_CELLULE
                    by = y * TAILLE_CELLULE
                    if bx + TAILLE_CELLULE < px or bx > px + projectile.largeur:
                        continue
                    if by + TAILLE_CELLULE < py or by > py + projectile.hauteur:
                        continue
                    offset = (bx - px, by - py)
                    if proj_mask.overlap(bloc_mask, offset) is not None:
                        return True

        for plat in self.platformes_mobiles:
            pr = plat.obtenir_rect()
            if not proj_rect.colliderect(pr):
                continue
            bloque = False
            if plat.couleur is None or plat.couleur == "noir":
                bloque = True
            elif couleur_joueur and plat.couleur == couleur_joueur:
                bloque = True
            if bloque:
                p_mask = pygame.Mask((pr.width, pr.height), fill=True)
                offset = (pr.x - px, pr.y - py)
                if proj_mask.overlap(p_mask, offset) is not None:
                    return True
        return False

    def bloc_solide_au_dessus(self, joueur):
        """Vérifie s'il y a un bloc solide juste au-dessus du joueur"""
        # Zone de détection au-dessus de la tête du joueur
        head_y = joueur.y + joueur.marge_y_haut
        detection_height = 10
        
        detection_rect = pygame.Rect(
            joueur.x + joueur.marge_x + 5,
            head_y - detection_height,
            joueur.largeur - 2 * joueur.marge_x - 10,
            detection_height
        )
        
        # blocs solides
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                if bloc == "noir" or (bloc in ["rouge", "bleu", "vert", "gris"] and bloc == joueur.couleur):
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if detection_rect.colliderect(bloc_rect):
                        return True
        
        # collision avec plateformes mobiles
        for plat in self.platformes_mobiles:
            # Ignorer si les plateformes de couleur différente
            if plat.couleur is not None and plat.couleur != "noir" and plat.couleur != joueur.couleur:
                continue
            pr = plat.obtenir_rect()
            if detection_rect.colliderect(pr):
                return True
        
        return False
    
    def dessiner(self, ecran, temps_global=0, update_entities=True):
        """Dessine tous les blocs du niveau"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                if bloc != "vide":
                    if bloc == "porte" and self.image_porte:
                        # Dessiner l'image du portail d'arrivée sur 2 blocs de hauteur
                        image_porte_haute = pygame.transform.scale(self.image_porte, (TAILLE_CELLULE, TAILLE_CELLULE * 1.4))
                        ecran.blit(image_porte_haute, (x * TAILLE_CELLULE, y * TAILLE_CELLULE - TAILLE_CELLULE * 0.4))
                    
                    elif "change_" in bloc:
                        # Afficher la potion correspondante avec l'effet bobbing
                        img_port = self.images_potion.get(bloc)
                        base_lift, bob = self.obtenir_decalage_potion(x, y)
                        if img_port:
                            img2 = img_port
                            px = x * TAILLE_CELLULE + (TAILLE_CELLULE - img2.get_width()) // 2
                            py = int(y * TAILLE_CELLULE + (TAILLE_CELLULE - img2.get_height()) / 2 - bob - base_lift)
                            ecran.blit(img2, (px, py))
                    
                    else:
                        # Blocs normaux
                        couleur = COULEURS[bloc]
                        pygame.draw.rect(ecran, couleur, (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
        
        if update_entities:
            # mise à jour plateformes
            self.maj_plateformes(temps_global)
            for plat in list(self.platformes_mobiles):
                plat.dessiner(ecran)
            
            for sorcier in list(self.sorciers):
                proj = sorcier.update()
                if proj is not None:
                    self.projectiles.append(proj)
                    random.choice(self.sons_sorcier_shot).play()
                # appliquer le déplacement de la plateforme si le sorcier est sur/contre une plateforme
                self.appliquer_pousse_plateforme_sur_entite(sorcier)
                sorcier.dessiner(ecran)

            for squelette in list(self.squelettes):
                ancien_etat = squelette.state
                squelette.update()
                # Jouer un son quand le squelette commence à attaquer
                if squelette.state == "attacking" and ancien_etat == "pre_attack":
                    random.choice(self.sons_squelette_tape).play()
                self.appliquer_pousse_plateforme_sur_entite(squelette)
                squelette.dessiner(ecran)

            proj_list = list(self.projectiles)
            for proj in proj_list:
                proj.update()
                proj_alive = proj.alive
                if not proj_alive:
                    self.projectiles.remove(proj)
                else:
                    proj.dessiner(ecran)

            for slime in list(self.slimes):
                slime.update()
                if not slime.alive:
                    self.appliquer_drop(slime)
                    self.slimes.remove(slime)
                else:
                    self.appliquer_pousse_plateforme_sur_entite(slime)
                    slime.dessiner(ecran)

            for piece in list(self.pieces):
                piece.update()
                if not piece.alive:
                    self.pieces.remove(piece)
                else:
                    self.appliquer_pousse_plateforme_sur_entite(piece)
                    piece.dessiner(ecran)

            for feu in self.feux:
                self.appliquer_pousse_plateforme_sur_entite(feu)
                feu.dessiner(ecran, self.frames_feu, self.frames_fumee, temps_global, TAILLE_CELLULE)

            for pic in self.pics:
                self.appliquer_pousse_plateforme_sur_entite(pic)
                pic.dessiner(ecran, self.image_pic)

            # Power ups de feu
            self.tenter_spawn_cristal_feu()
            for cristal in list(self.cristaux_feu):
                    cristal.update()
                    if not cristal.alive:
                        self.cristaux_feu.remove(cristal)
                    else:
                        cristal.dessiner(ecran)

            # Projectiles du joueur
            for pf in list(self.projectiles_joueur):
                pf.update()
                if not pf.alive:
                    self.projectiles_joueur.remove(pf)
                else:
                    pf.dessiner(ecran)

            # Démons
            for demon in self.demons:
                demon.dessiner(ecran)

            # Boss et ses projectiles
            if self.boss is not None:
                self.boss.dessiner(ecran)
            for bp in self.projectiles_boss:
                bp.dessiner(ecran)
            for dp in self.projectiles_demon:
                dp.dessiner(ecran)

        else:
            for plat in self.platformes_mobiles:
                plat.dessiner(ecran)
            for sorcier in self.sorciers:
                sorcier.dessiner(ecran)
            for squelette in self.squelettes:
                squelette.dessiner(ecran)
            for proj in self.projectiles:
                proj.dessiner(ecran)
            for slime in self.slimes:
                slime.dessiner(ecran)
            for piece in self.pieces:
                piece.dessiner(ecran)
            for feu in self.feux:
                feu.dessiner(ecran, self.frames_feu, self.frames_fumee, temps_global, TAILLE_CELLULE)
            for pic in self.pics:
                pic.dessiner(ecran, self.image_pic)
            for pu in self.cristaux_feu:
                pu.dessiner(ecran)
            for pf in self.projectiles_joueur:
                pf.dessiner(ecran)
            for demon in self.demons:
                demon.dessiner(ecran)
            if self.boss is not None:
                self.boss.dessiner(ecran)
            for bp in self.projectiles_boss:
                bp.dessiner(ecran)
            for dp in self.projectiles_demon:
                dp.dessiner(ecran)

    def dessiner_fond(self, ecran, couleur_planete, temps_global=0):
        """Dessine le fond pour le niveau basé sur la couleur de la planète.
        """
        # dégradé du ciel
        for y in range(HAUTEUR_ECRAN):
            ratio = y / HAUTEUR_ECRAN
            r = int(10 + ratio * couleur_planete[0] * 0.3)
            g = int(10 + ratio * couleur_planete[1] * 0.3)
            b = int(30 + ratio * couleur_planete[2] * 0.3)
            pygame.draw.line(ecran, (r, g, b), (0, y), (LARGEUR_ECRAN, y))

        # dessiner les étoiles scintillantes
        for etoile in self.etoiles_fond:
            x, y, taille, brillance_base, vitesse, phase = etoile
            brillance = int(brillance_base * 0.5 * (0.5 + 0.5 * math.sin(temps_global * vitesse + phase)))
            brillance = max(30, min(180, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (int(x), int(y)), taille)
    
    def dessiner_portail(self, ecran, x, y, taille, temps_global):
        """Dessine un portail de téléportation jaune"""
        
        # Effet de rotation et pulsation
        pulse = 1 + 0.2 * math.sin(temps_global * 0.03)
        rayon = int(taille * pulse)
        
        # Cercles pour l'effet de portail
        for i in range(5):
            alpha = 180 - i * 35
            r = rayon - i * (rayon // 6)
            if r > 0:
                teinte = 200 + int(55 * math.sin(temps_global * 0.02 + i))
                surface = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, teinte, 50, alpha), (r + 5, r + 5), r)
                ecran.blit(surface, (x - r - 5, y - r - 5))
        
        # Particules tourbillonnantes
        for i in range(8):
            angle = temps_global * 0.015 + i * (math.pi / 4)
            dist = rayon * 0.7
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            particle_size = 3 + int(2 * math.sin(temps_global * 0.04 + i))
            pygame.draw.circle(ecran, (255, 255, 150), (px, py), particle_size)
        
        pygame.draw.circle(ecran, (255, 255, 200), (x, y), rayon // 4)

    def maj_plateformes(self, tick):
        """Met à jour toutes les plateformes mobiles."""
        if tick == self.dernier_tick_maj_plat:
            return
        self.dernier_tick_maj_plat = tick
        for plat in self.platformes_mobiles:
            plat.maj()

    def appliquer_pousse_plateforme_sur_entite(self, entite):
        """Applique le déplacement d'une plateforme mobile à une entité si elle est debout dessus."""

        rect_ent = entite.rect
        for plat in self.platformes_mobiles:
            rect_plat = plat.obtenir_rect()
            dx = plat.dernier_dx
            dy = plat.dernier_dy

            # Vérifier si l'entité est debout sur la plateforme
            pieds_bottom = rect_ent.bottom
            
            if dy > 0:
                tolerance = dy + 2
            else:
                tolerance = 4
                
            chevauchement_horizontal = False
            if rect_ent.right > rect_plat.left and rect_ent.left < rect_plat.right:
                chevauchement_horizontal = True
                
            distance_verticale = pieds_bottom - rect_plat.top
            if distance_verticale < 0:
                distance_verticale = -distance_verticale
                
            if chevauchement_horizontal and distance_verticale <= tolerance:
                entite.x = entite.x + dx
                entite.y = entite.y + dy
                entite.rect.x = entite.rect.x + dx
                entite.rect.y = entite.rect.y + dy
                if entite.visual_x is not None:
                    entite.visual_x = entite.visual_x + dx
                    entite.visual_y = entite.visual_y + dy
                break
        return

    def pousser_demon_par_plateformes(self, demon, couleur):
        """Pousse le démon hors d'une plateforme mobile qui lui rentre dedans."""
        demon.maj_rect()
        for plat in self.platformes_mobiles:
            # plateforme solide seulement pour la couleur du mage
            if plat.couleur is not None and plat.couleur != "noir" and plat.couleur != couleur:
                continue
            rect_plat = plat.obtenir_rect()
            if not demon.rect.colliderect(rect_plat):
                continue
            dx = plat.dernier_dx
            dy = plat.dernier_dy
            avant_x = demon.x
            avant_y = demon.y
            # coller le démon contre le bord dans le sens du déplacement
            if dx > 0:
                demon.x = rect_plat.right - demon.marge_x
            elif dx < 0:
                demon.x = rect_plat.left - (demon.width - demon.marge_x)
            if dy > 0:
                demon.y = rect_plat.bottom - demon.marge_y_haut
            elif dy < 0:
                demon.y = rect_plat.top - (demon.height - demon.marge_y_bas)
            demon.decaler_ancres(demon.x - avant_x, demon.y - avant_y)
            demon.maj_rect()
        return

    def appliquer_pousse_plateforme(self, joueur):
        """collision"""
        rect_joueur = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
        dx_deja_applique = set()

        for plat in self.platformes_mobiles:
            # gestion des interactions de  couleurs
            if plat.couleur is not None and plat.couleur != "noir" and plat.couleur != joueur.couleur:
                continue

            rect_plat = plat.obtenir_rect()
            dx = plat.dernier_dx
            dy = plat.dernier_dy

            # écrasement
            if dy > 0 and rect_joueur.colliderect(rect_plat):
                tete_top = joueur.y + joueur.marge_y_haut
                if tete_top <= rect_plat.bottom - 5:
                    if self.bloc_solide_au_dessus(joueur):
                        return "mort"

                    ancien_plateforme = rect_plat.copy()
                    ancien_plateforme.move_ip(-dx, -dy)
                    if not ancien_plateforme.colliderect(rect_joueur):
                        player_vy = joueur.vitesse_y
                        if player_vy < 0:
                            magnitude_montante = -player_vy
                        else:
                            magnitude_montante = 0
                        if magnitude_montante > abs(dy) + 1:
                            joueur.y = rect_plat.bottom - joueur.marge_y_haut
                            joueur.vitesse_y = 0

            # collision
            if rect_joueur.colliderect(rect_plat):
                cle = (dx, dy)
                if cle not in dx_deja_applique:
                    old_x = joueur.x
                    old_y = joueur.y
                    joueur.x += dx
                    if dy != 0:
                        joueur.y += dy

                    rect_test = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)

                    if self.collision(rect_test, joueur.couleur):
                        joueur.x = old_x
                        rect_test_x = pygame.Rect(joueur.x + joueur.marge_x, old_y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
                        if not self.collision(rect_test_x, joueur.couleur):
                            joueur.y = old_y + dy
                        else:
                            joueur.x = old_x
                            joueur.y = old_y

                    rect_joueur.topleft = (joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut)
                    if dx != 0 or dy != 0:
                        joueur.pousse_plateforme = True
                    dx_deja_applique.add(cle)
                continue

            # debout
            pieds_bottom = joueur.y + joueur.hauteur - joueur.marge_y_bas
            tolerance = 6
            chevauchement_horizontal = not (rect_joueur.right <= rect_plat.left or rect_joueur.left >= rect_plat.right)
            if chevauchement_horizontal and (rect_plat.top - tolerance <= pieds_bottom <= rect_plat.top + 2):
                cle = (dx, dy)
                if cle not in dx_deja_applique:
                    old_x = joueur.x
                    old_y = joueur.y
                    joueur.x += dx
                    if dy != 0:
                        joueur.y += dy

                    rect_test = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
                    if self.collision(rect_test, joueur.couleur):
                        joueur.x = old_x
                        joueur.y = old_y
                    else:
                        joueur.pousse_plateforme = True
                    dx_deja_applique.add(cle)

                    if joueur.vitesse_y >= 0:
                        joueur.au_sol = True

                    rect_joueur.topleft = (joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut)
