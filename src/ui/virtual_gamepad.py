import pygame
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN
from core.assets import police
import core.i18n as i18n


class VirtualGamepad:
    """Contrôles tactiles : joystick (fixe ou dynamique) à gauche, boutons saut/tir à droite."""

    def __init__(self, fixe=False):
        # Devient True au premier toucher
        self.actif = False
        self.fixe = fixe

        self.gauche_presse = False
        self.droite_presse = False
        self.saut_presse = False
        self.tir_presse = False
        self.peut_tirer_active = False

        # Joystick : position d'affichage  + position du manche
        self.position_fixe = (170, HAUTEUR_ECRAN - 130)
        self.joystick_origine = self.position_fixe
        self.joystick_actuel = self.position_fixe
        self.joystick_id = None
        # Toujours affiché en mode tactile
        self.joystick_visible = True
        self.rayon_joystick = 90
        self.zone_morte = 25

        # Boutons fixes en bas à droite
        self.rayon_bouton = 75
        self.bouton_saut = (LARGEUR_ECRAN - 130, HAUTEUR_ECRAN - 130)
        self.bouton_tir = (LARGEUR_ECRAN - 300, HAUTEUR_ECRAN - 95)
        self.doigts_boutons = {}

        self.font = police(50)

    def definir_mode(self, fixe):
        """Bascule entre joystick fixe et dynamique."""
        self.fixe = fixe
        self.reset()

    def reset(self):
        """Replace le joystick à sa position de départ (début de niveau)."""
        self.joystick_origine = self.position_fixe
        self.joystick_actuel = self.position_fixe
        self.joystick_id = None
        self.joystick_visible = True

    def clamper_origine(self):
        """Garde le joystick entièrement à l'écran, sur la moitié gauche."""
        marge = self.rayon_joystick + 10
        ox = max(marge, min(LARGEUR_ECRAN // 2, self.joystick_origine[0]))
        oy = max(marge, min(HAUTEUR_ECRAN - marge, self.joystick_origine[1]))
        self.joystick_origine = (ox, oy)

    def gerer_evenement(self, evenement):
        """Traite un événement tactile (FINGERDOWN/MOTION/UP)."""
        if evenement.type not in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            return

        self.actif = True
        finger_id = evenement.finger_id
        x = evenement.x * LARGEUR_ECRAN
        y = evenement.y * HAUTEUR_ECRAN

        if evenement.type == pygame.FINGERDOWN:
            self.toucher(finger_id, x, y)
        elif evenement.type == pygame.FINGERMOTION:
            self.bouger(finger_id, x, y)
        else:
            self.relacher(finger_id)

        self.maj_etats()

    def toucher(self, finger_id, x, y):
        """Un doigt se pose : bouton, ou joystick si moitié gauche."""
        nom = self.bouton_sous(x, y)
        if nom is not None:
            self.doigts_boutons[finger_id] = nom
            return
        if x < LARGEUR_ECRAN // 2:
            self.joystick_id = finger_id
            if self.fixe:
                self.joystick_origine = self.position_fixe
            else:
                # le joystick apparaît sous le doigt
                self.joystick_origine = (x, y)
                self.joystick_visible = True
            self.clamper_origine()
            self.joystick_actuel = (x, y)

    def bouger(self, finger_id, x, y):
        """Un doigt bouge : le manche suit, et en dynamique la base suit aussi."""
        if finger_id != self.joystick_id:
            return
        self.joystick_actuel = (x, y)
        # En dynamique, si le doigt dépasse le rayon, la base le suit dans cette direction
        if not self.fixe:
            dx = x - self.joystick_origine[0]
            dy = y - self.joystick_origine[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > self.rayon_joystick:
                self.joystick_origine = (x - dx / dist * self.rayon_joystick, y - dy / dist * self.rayon_joystick)
                self.clamper_origine()

    def relacher(self, finger_id):
        """Un doigt se lève : le joystick revient à sa position de base."""
        if finger_id == self.joystick_id:
            self.joystick_id = None
            self.joystick_origine = self.position_fixe
            self.joystick_actuel = self.position_fixe
        if finger_id in self.doigts_boutons:
            del self.doigts_boutons[finger_id]

    def bouton_sous(self, x, y):
        """Retourne le nom du bouton sous (x, y), ou None."""
        if self.distance(x, y, self.bouton_saut) <= self.rayon_bouton * 1.3:
            return "saut"
        if self.peut_tirer_active and self.distance(x, y, self.bouton_tir) <= self.rayon_bouton * 1.3:
            return "tir"
        return None

    def distance(self, x, y, centre):
        dx = x - centre[0]
        dy = y - centre[1]
        return (dx * dx + dy * dy) ** 0.5

    def maj_etats(self):
        """Recalcule les états gauche/droite/saut/tir."""
        self.gauche_presse = False
        self.droite_presse = False
        if self.joystick_id is not None:
            dx = self.joystick_actuel[0] - self.joystick_origine[0]
            if dx < -self.zone_morte:
                self.gauche_presse = True
            elif dx > self.zone_morte:
                self.droite_presse = True

        boutons_tenus = set(self.doigts_boutons.values())
        self.saut_presse = "saut" in boutons_tenus
        self.tir_presse = "tir" in boutons_tenus

    def dessiner(self, surface):
        if self.joystick_visible:
            cx = int(self.joystick_origine[0])
            cy = int(self.joystick_origine[1])
            self.dessiner_cercle(surface, cx, cy, self.rayon_joystick, (255, 255, 255, 40))
            dx = self.joystick_actuel[0] - self.joystick_origine[0]
            dy = self.joystick_actuel[1] - self.joystick_origine[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > self.rayon_joystick:
                dx = dx / dist * self.rayon_joystick
                dy = dy / dist * self.rayon_joystick
            self.dessiner_cercle(surface, int(cx + dx), int(cy + dy), 45, (255, 255, 255, 110))

        if i18n.langue_actuelle == "fr":
            lettre_saut = "S"
            lettre_tir = "T"
        else:
            lettre_saut = "J"
            lettre_tir = "S"
        
        self.dessiner_bouton(surface, self.bouton_saut, lettre_saut, self.saut_presse)
        if self.peut_tirer_active:
            self.dessiner_bouton(surface, self.bouton_tir, lettre_tir, self.tir_presse)

    def dessiner_bouton(self, surface, centre, lettre, presse):
        if presse:
            couleur = (255, 255, 255, 130)
        else:
            couleur = (255, 255, 255, 40)
        self.dessiner_cercle(surface, centre[0], centre[1], self.rayon_bouton, couleur)
        txt = self.font.render(lettre, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=centre))

    def dessiner_cercle(self, surface, x, y, rayon, couleur):
        temp = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, couleur, (rayon, rayon), rayon)
        pygame.draw.circle(temp, (255, 255, 255, 90), (rayon, rayon), rayon, 4)
        surface.blit(temp, (x - rayon, y - rayon))
