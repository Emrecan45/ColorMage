import pygame
import core.temps as temps
import os

from core.config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT, LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import charger_image


cache_projectile = {}


import math
from core.config import TAILLE_CELLULE

cache_piece = {}


def construire_frames_piece(taille_affichage):
    if taille_affichage in cache_piece:
        return cache_piece[taille_affichage]
    sprite_w = 16
    sprite_h = 16
    sheet = charger_image(resource_path(os.path.join("assets/img/items", "piece.png")), "alpha")
    nb_frames = sheet.get_width() // sprite_w
    frames = []
    for i in range(nb_frames):
        sprite = sheet.subsurface(pygame.Rect(i * sprite_w, 0, sprite_w, sprite_h))
        frames.append(pygame.transform.scale(sprite, (taille_affichage, taille_affichage)))
    cache_piece[taille_affichage] = frames
    return frames


class Piece:
    """Pièce qui tourne sur elle-même."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visual_x = None
        self.visual_y = None
        self.alive = True
        self.cell_x = None
        self.cell_y = None

        # Taille d'affichage
        self.taille_affichage = int(TAILLE_CELLULE * 0.7)

        # Frames
        self.frames = construire_frames_piece(self.taille_affichage)

        self.frame_index = 0
        self.last_anim_time = temps.obtenir_temps()
        self.anim_delay = 80

        # Hitbox et dessin
        self.offset = (TAILLE_CELLULE - self.taille_affichage) // 2
        self.draw_x = self.x + self.offset
        self.draw_y = self.y + self.offset
        self.rect = pygame.Rect(self.draw_x, self.draw_y, self.taille_affichage, self.taille_affichage)
        
        # Physique
        self.v_x = 0
        self.v_y = 0
        self.y_sol = None
        self.au_sol = False

    def update(self):
        now = temps.obtenir_temps()
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Physique
        if self.y_sol is not None and not self.au_sol:
            self.v_y += 0.5  # gravité
            self.x += self.v_x
            self.y += self.v_y
            
            # Rebond sur le sol
            if self.y + self.offset + self.taille_affichage >= self.y_sol:
                self.y = self.y_sol - self.offset - self.taille_affichage
                if abs(self.v_y) < 1.5:
                    self.v_y = 0
                    self.v_x = 0
                    self.au_sol = True
                else:
                    self.v_y = -self.v_y * 0.5
                    self.v_x *= 0.8
            
            self.draw_x = self.x + self.offset
            self.draw_y = self.y + self.offset
            self.rect.topleft = (self.draw_x, self.draw_y)

    def dessiner(self, ecran):
        frame = self.frames[self.frame_index]
        ecran.blit(frame, (int(self.draw_x), int(self.draw_y)))



cache_cristal = {}


def construire_assets_cristal():
    """Construit une seule fois les frames et masques du cristal."""
    if "assets" in cache_cristal:
        return cache_cristal["assets"]
    cible = 40
    chemin = resource_path(os.path.join("assets/img/items", "cristal_feu.png"))
    spritesheet = charger_image(chemin, "convert").copy()
    spritesheet.set_colorkey((0, 0, 0))

    crop_y = 151
    crop_h = 88
    segments = [(22, 113), (125, 198), (215, 265), (287, 306),
                (328, 388), (402, 473), (489, 574)]

    frames = []
    for (x_debut, x_fin) in segments:
        largeur = x_fin - x_debut + 1
        sprite_source = spritesheet.subsurface(pygame.Rect(x_debut, crop_y, largeur, crop_h))
        rapport = min(cible / largeur, cible / crop_h)
        nouvelle_largeur = max(1, int(largeur * rapport))
        nouvelle_hauteur = max(1, int(crop_h * rapport))
        echelle = pygame.transform.scale(sprite_source, (nouvelle_largeur, nouvelle_hauteur))
        res = pygame.Surface((cible, cible), pygame.SRCALPHA)
        res.fill((0, 0, 0, 0))
        res.blit(echelle, ((cible - nouvelle_largeur) // 2, (cible - nouvelle_hauteur) // 2))
        frames.append(res)

    masks = []
    for f in frames:
        masks.append(pygame.mask.from_surface(f))
    cache_cristal["assets"] = {"frames": frames, "masks": masks}
    return cache_cristal["assets"]


class CristalFeu:
    """Cristal de feu ramassable qui donne au joueur le pouvoir de tir."""
    taille_affichage = 40

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visual_x = None
        self.visual_y = None
        self.alive = True

        a = construire_assets_cristal()
        self.frames = a["frames"]
        self.masks = a["masks"]
        self.nb_frames = len(self.frames)

        self.frame_index = 0
        self.last_anim_time = temps.obtenir_temps()
        self.anim_delay = 80

        self.current_draw_x = int(self.x - self.taille_affichage // 2)
        self.current_draw_y = int(self.y - self.taille_affichage // 2)
        self.current_mask = self.masks[self.frame_index]
        self.rect = pygame.Rect(self.current_draw_x, self.current_draw_y, self.taille_affichage, self.taille_affichage)

    def update(self):
        now = temps.obtenir_temps()
        if now - self.last_anim_time >= self.anim_delay:
            self.last_anim_time = now
            self.frame_index = (self.frame_index + 1) % self.nb_frames
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


