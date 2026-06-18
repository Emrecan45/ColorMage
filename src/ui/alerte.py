import pygame
import os
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, resource_path


class Alerte:
    """Petite notification en bas à droite qui glisse puis disparaît"""

    def __init__(self, gestionnaire_config=None):
        self.font = pygame.font.SysFont(None, 32)
        self.actif = False
        self.texte = ""
        self.timer = 0
        self.duree = 360  # durée totale en frames
        self.duree_glisse = 20
        self.marge = 15
        self.hauteur = 50
        self.largeur = 0
        self.x = 0
        self.y = HAUTEUR_ECRAN - self.hauteur - self.marge

        self.gestionnaire_config = gestionnaire_config
        self.son_alerte = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "alerte.wav")))
        self.maj_volume()

    def maj_volume(self):
        """Applique le volume des effets au son d'alerte."""
        if self.gestionnaire_config is not None:
            vol = self.gestionnaire_config.volumes.get("effets", 50) / 100
            self.son_alerte.set_volume(vol)

    def afficher(self, texte):
        """Lance une alerte avec le texte donné"""
        self.texte = texte
        self.actif = True
        self.timer = 0
        self.son_alerte.play()
        surface_texte = self.font.render(self.texte, True, (255, 255, 255))
        self.largeur = surface_texte.get_width() + 40
        self.x = LARGEUR_ECRAN

    def mise_a_jour(self):
        """Met à jour l'animation de l'alerte"""
        if not self.actif:
            return

        self.timer += 1

        x_visible = LARGEUR_ECRAN - self.largeur - self.marge
        x_cache = LARGEUR_ECRAN

        if self.timer <= self.duree_glisse:
            progression = self.timer / self.duree_glisse
            self.x = x_cache + (x_visible - x_cache) * progression
        elif self.timer <= self.duree - self.duree_glisse:
            self.x = x_visible
        elif self.timer <= self.duree:
            progression = (self.timer - (self.duree - self.duree_glisse)) / self.duree_glisse
            self.x = x_visible + (x_cache - x_visible) * progression
        else:
            self.actif = False

    def dessiner(self, ecran):
        """Dessine l'alerte sur l'écran"""
        if not self.actif:
            return

        self.mise_a_jour()

        rect = pygame.Rect(int(self.x), self.y, self.largeur, self.hauteur)

        # Fond
        pygame.draw.rect(ecran, (50, 50, 70), rect, border_radius=10)

        # Bordure
        pygame.draw.rect(ecran, (255, 200, 50), rect, 3, border_radius=10)

        # Texte
        surface_texte = self.font.render(self.texte, True, (255, 255, 255))
        tx = rect.x + (rect.width - surface_texte.get_width()) // 2
        ty = rect.y + (rect.height - surface_texte.get_height()) // 2
        ecran.blit(surface_texte, (tx, ty))
