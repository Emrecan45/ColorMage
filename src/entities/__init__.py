import pygame
import os
import math
import random

from core.config import TAILLE_CELLULE, resource_path, VITESSE_DEPLACEMENT, LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import charger_image

from entities.boss.boss import Boss
from entities.projectiles import Projectile, ProjectileFeu, ProjectilePyro, ProjectileDemon, construire_assets_projectile, construire_assets_feu, charger_frames_pyro_projectile, charger_assets_projectile_demon
from entities.monstres import Sorcier, Squelette, Slime, Demon, construire_frames_sorcier, construire_masques_sorcier, construire_assets_squelette, construire_frames_slime, construire_assets_demon, DEMON_W, DEMON_H
from entities.objets import Piece, CristalFeu, construire_frames_piece, construire_assets_cristal
from entities.boss.pyrolord import Pyrolord, charger_assets_pyrolord

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


def etapes_prechargement():
    """Retourne les étapes de préchargement des ennemis sous forme."""
    taille_ennemi = TAILLE_CELLULE * 2
    petit_slime = int(TAILLE_CELLULE * 1.5)
    taille_piece = int(TAILLE_CELLULE * 0.7)
    etapes = []
    etapes.append((construire_assets_projectile, (45,)))
    etapes.append((construire_assets_projectile, (100,)))
    etapes.append((construire_frames_sorcier, (taille_ennemi, taille_ennemi)))
    etapes.append((construire_masques_sorcier, (taille_ennemi, taille_ennemi)))
    etapes.append((construire_assets_squelette, (taille_ennemi, taille_ennemi)))
    etapes.append((construire_frames_slime, ("vert", petit_slime)))
    etapes.append((construire_frames_slime, ("violet", petit_slime)))
    etapes.append((construire_assets_demon, (DEMON_W, DEMON_H)))
    etapes.append((charger_assets_projectile_demon, ()))
    etapes.append((construire_frames_piece, (taille_piece,)))
    etapes.append((construire_assets_feu, ()))
    etapes.append((construire_assets_cristal, ()))
    etapes.append((charger_frames_pyro_projectile, ()))
    etapes.append((charger_assets_pyrolord, (Pyrolord.ECHELLE,)))
    etapes.append((charger_assets_pyrolord, (Pyrolord.ECHELLE_BOSS,)))
    etapes.append((charger_assets_pyrolord, (Pyrolord.ECHELLE_BOSS * Pyrolord.ENRAGE_SCALE,)))
    return etapes

