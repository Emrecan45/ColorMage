import pygame

temps_jeu = 0
dernier_temps_reel = 0
en_pause = False

def init():
    global temps_jeu, dernier_temps_reel, en_pause
    temps_jeu = 0
    dernier_temps_reel = pygame.time.get_ticks()
    en_pause = False

def update():
    global temps_jeu, dernier_temps_reel, en_pause
    maintenant = pygame.time.get_ticks()
    if not en_pause:
        temps_jeu = temps_jeu + (maintenant - dernier_temps_reel)
    dernier_temps_reel = maintenant

def set_pause(pause_active):
    global en_pause, dernier_temps_reel
    if not pause_active and en_pause:
        dernier_temps_reel = pygame.time.get_ticks()
    en_pause = pause_active

def obtenir_temps():
    return temps_jeu


def avancer(ms):
    """Avance le temps de jeu d'un pas fixe (rattrapage de frames)."""
    global temps_jeu, dernier_temps_reel
    if not en_pause:
        temps_jeu = temps_jeu + ms
    dernier_temps_reel = pygame.time.get_ticks()
