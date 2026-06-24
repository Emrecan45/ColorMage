import pygame
import os
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE, EST_WEB, resource_path
from core.son import Son
from core.assets import police, position_centree
from core.i18n import t
from core.config_manager import ConfigManager

class Menu:
    """Menu du jeu"""

    def __init__(self, gestionnaire_config=None):
        self.font_1 = police(50)
        self.font_2 = police(40)
        
        # Charger l'image de fond
        self.fond = pygame.image.load(resource_path("assets/img/ui/fond_menu1.png")).convert_alpha()
        self.fond = pygame.transform.scale(self.fond, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        
        # Charger l'icône de profil (conserver les proportions)
        try:
            self.icone_profil = pygame.image.load(resource_path("assets/img/ui/profile.png")).convert_alpha()
            # L'image fait 677x369, on garde les proportions pour 55px de haut
            ratio = self.icone_profil.get_width() / self.icone_profil.get_height()
            nouvelle_hauteur = 55
            nouvelle_largeur = int(nouvelle_hauteur * ratio)
            self.icone_profil = pygame.transform.smoothscale(self.icone_profil, (nouvelle_largeur, nouvelle_hauteur))
        except:
            self.icone_profil = None
        
        if EST_WEB:
            decalage = 40
        else:
            decalage = 0
        self.bouton_jouer = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 - 60 + decalage, 250, 50)
        self.bouton_grimoire = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 20 + decalage, 250, 50)
        self.bouton_parametres = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 100 + decalage, 250, 50)
        self.bouton_quitter = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 180, 250, 50)
        self.bouton_profil = pygame.Rect(LARGEUR_ECRAN - 100, 15, 80, 80)
        
        # son des clics
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.son_select = Son(resource_path(os.path.join("assets/audio", "select.wav")))
        self.maj_volume()
    
    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.volumes
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
    
    def dessiner_bouton_arrondi(self, ecran, rect, couleur, texte, font):
        """Dessine un bouton avec des bords arrondis"""
        pygame.draw.rect(ecran, couleur, rect, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, rect, 3, border_radius=10)
        
        texte_surface = font.render(texte, True, (255, 255, 255))
        ecran.blit(texte_surface, position_centree(texte_surface, font, rect.centerx, rect.centery))
    
    def afficher_menu(self, ecran):
        """Affiche le menu"""
        # Mettre à jour le volume à chaque affichage
        self.maj_volume()
        
        # Afficher l'image de fond
        ecran.blit(self.fond, (0, 0))
        
        # version du jeu
        version_txt = self.font_2.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))
        
        # Dessiner les boutons avec bords arrondis
        mouse_pos = pygame.mouse.get_pos()
        
        # Bouton Jouer
        if self.bouton_jouer.collidepoint(mouse_pos):
            couleur_jouer = COULEUR_SURVOL
        else:
            couleur_jouer = COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_jouer, couleur_jouer, t("menu.jouer"), self.font_1)
        
        # Bouton Grimoire
        if self.bouton_grimoire.collidepoint(mouse_pos):
            couleur_grimoire = COULEUR_SURVOL
        else:
            couleur_grimoire = COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_grimoire, couleur_grimoire, t("menu.grimoire"), self.font_1)
        
        # Bouton Paramètres
        if self.bouton_parametres.collidepoint(mouse_pos):
            couleur_param = COULEUR_SURVOL
        else:
            couleur_param = COULEUR_BOUTON
        self.dessiner_bouton_arrondi(ecran, self.bouton_parametres, couleur_param, t("menu.parametres"), self.font_1)
        
        # Bouton Quitter
        if not EST_WEB:
            if self.bouton_quitter.collidepoint(mouse_pos):
                couleur_quitter = (150, 50, 50)
            else:
                couleur_quitter = (120, 30, 30)
            self.dessiner_bouton_arrondi(ecran, self.bouton_quitter, couleur_quitter, t("menu.quitter"), self.font_1)
        
        # Bouton Profil (en haut à droite avec icône)
        if self.bouton_profil.collidepoint(mouse_pos):
            couleur_profil = COULEUR_SURVOL
        else:
            couleur_profil = COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur_profil, self.bouton_profil, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_profil, 2, border_radius=10)
        if self.icone_profil:
            icone_x = self.bouton_profil.centerx - self.icone_profil.get_width() // 2
            icone_y = self.bouton_profil.centery - self.icone_profil.get_height() // 2
            ecran.blit(self.icone_profil, (icone_x, icone_y))
        
        return None
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "jouer" ou "parametres" ou "quitter" ou "profil" ou None
        """
        if self.bouton_profil.collidepoint(pos):
            self.son_select.play()
            return "profil"
        if self.bouton_jouer.collidepoint(pos):
            self.son_select.play()
            return "jouer"
        elif self.bouton_grimoire.collidepoint(pos):
            self.son_select.play()
            return "grimoire"
        elif self.bouton_parametres.collidepoint(pos):
            self.son_select.play()
            return "parametres"
        elif not EST_WEB and self.bouton_quitter.collidepoint(pos):
            self.son_select.play()
            pygame.time.wait(500)
            return "quitter"
        return None
