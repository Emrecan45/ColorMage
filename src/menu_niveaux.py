import pygame
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU
from config_manager import ConfigManager

class MenuNiveaux:
    """Menu de sélection des niveaux"""

    def __init__(self):
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)
        
        self.gestionnaire_config = ConfigManager()
        self.config = self.gestionnaire_config.charger_config()
        self.niveau_max_debloque = self.config["niveau_actuel"]
        self.nombre_niveaux = 10
        
        self.boutons_niveaux = []
        for i in range(self.nombre_niveaux):
            largeur = LARGEUR_ECRAN // 6 + (i % 8) * 100
            hauteur = HAUTEUR_ECRAN // 4 + (i // 8) * 100
            self.boutons_niveaux.append(pygame.Rect(largeur, hauteur, 80, 80))
        
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN - 100, 250, 50)
        
        self.image_cadenas = pygame.image.load("img/cadena.png")
        self.image_cadenas = pygame.transform.scale(self.image_cadenas, (40, 40))
    
    def afficher_selection(self, ecran):
        self.config = self.gestionnaire_config.charger_config()
        self.niveau_max_debloque = self.config["niveau_actuel"]
        
        ecran.fill((0, 0, 0))
        
        titre_txt = self.font_1.render("Niveaux", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, 50))
        
        for i in range(len(self.boutons_niveaux)):
            bouton = self.boutons_niveaux[i]
            niveau_numero = i + 1
            
            if niveau_numero <= self.niveau_max_debloque :
                est_debloque = True
            else :
                est_debloque = False
            
            if est_debloque:
                couleur_bouton = (0, 100, 0)  # Vert foncé pour débloqué
            else:
                couleur_bouton = (50, 50, 50)  # Gris foncé pour verrouillé
            
            pygame.draw.rect(ecran, couleur_bouton, bouton)
            pygame.draw.rect(ecran, (255, 255, 255), bouton, 3)
            
            if est_debloque:
                numero_txt = self.font_1.render(str(niveau_numero), True, (255, 255, 255))
                ecran.blit(numero_txt, (bouton.centerx - numero_txt.get_width() // 2, bouton.centery - numero_txt.get_height() // 2))
            else:
                ecran.blit(self.image_cadenas, (bouton.centerx - 20, bouton.centery - 20))
        
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN - 90))
        
        version_txt = self.font_3.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))
    
    def gerer_clic(self, pos):
        for i in range(len(self.boutons_niveaux)):
            if self.boutons_niveaux[i].collidepoint(pos):
                niveau_numero = i + 1
                if niveau_numero <= self.niveau_max_debloque:
                    return niveau_numero
                else:
                    return None
        
        if self.bouton_retour.collidepoint(pos):
            return 0
        
        return None
