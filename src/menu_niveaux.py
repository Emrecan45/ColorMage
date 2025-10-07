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
        
        if "progression" not in self.config:
            self.config["progression"] = {"niveau_max_debloque": 1}
            self.gestionnaire_config.sauvegarder_config(self.config)
        
        self.niveau_max_debloque = self.config["progression"]["niveau_max_debloque"]
        self.nombre_niveaux = 10
        
        self.niveaux_par_ligne = 3
        self.taille_bouton = 100
        self.espacement = 40
        
        largeur_grille = self.niveaux_par_ligne * self.taille_bouton + (self.niveaux_par_ligne - 1) * self.espacement
        self.decalage_x = (LARGEUR_ECRAN - largeur_grille) // 2
        self.decalage_y = HAUTEUR_ECRAN // 2 - 100
        
        self.boutons_niveaux = []
        for i in range(self.nombre_niveaux):
            ligne = i // self.niveaux_par_ligne
            colonne = i % self.niveaux_par_ligne
            x = self.decalage_x + colonne * (self.taille_bouton + self.espacement)
            y = self.decalage_y + ligne * (self.taille_bouton + self.espacement)
            self.boutons_niveaux.append(pygame.Rect(x, y, self.taille_bouton, self.taille_bouton))
        
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN - 100, 250, 50)
    
    def afficher_selection(self, ecran):
        ecran.fill((0, 0, 0))
        
        titre_txt = self.font_1.render("Choisis un niveau", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, 50))
        
        for i in range(len(self.boutons_niveaux)):
            bouton = self.boutons_niveaux[i]
            couleur_bouton = (70, 130, 180)
            pygame.draw.rect(ecran, couleur_bouton, bouton)
            pygame.draw.rect(ecran, (255, 255, 255), bouton, 3)
            
            numero_txt = self.font_1.render(str(i + 1), True, (255, 255, 255))
            ecran.blit(numero_txt, (bouton.centerx - numero_txt.get_width() // 2, 
                                    bouton.centery - numero_txt.get_height() // 2))
        
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, 
                                HAUTEUR_ECRAN - 90))
        
        version_txt = self.font_3.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, 
                                 HAUTEUR_ECRAN - version_txt.get_height() - 20))
    
    def gerer_clic(self, pos):
        for i in range(len(self.boutons_niveaux)):
            if self.boutons_niveaux[i].collidepoint(pos):
                return i + 1
        
        if self.bouton_retour.collidepoint(pos):
            return None
        
        return 0
