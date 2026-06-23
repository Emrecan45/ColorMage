import os
import pygame
from core.config import EST_WEB

class Son:
    def __init__(self, chemin):
        self.nom = os.path.basename(chemin)
        self.volume = 1.0
        self.boucle = False
        if EST_WEB:
            import platform
            platform.window.colormage_load_sfx(self.nom)
            self.sound = None
        else:
            self.sound = pygame.mixer.Sound(chemin)

    def play(self, loops=0):
        if not EST_WEB:
            self.sound.play(loops)
            return
        if loops == -1:
            self.boucle = True
        else:
            self.boucle = False
        import platform
        platform.window.colormage_play_sfx(self.nom, self.volume, self.boucle)

    def set_volume(self, valeur):
        self.volume = valeur
        if not EST_WEB:
            self.sound.set_volume(valeur)
            return
        if self.boucle:
            import platform
            platform.window.colormage_set_sfx_volume(self.nom, valeur)

    def stop(self):
        if not EST_WEB:
            self.sound.stop()
            return
        import platform
        platform.window.colormage_stop_sfx(self.nom)
