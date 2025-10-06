import pygame
import sys
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""

    def __init__(self):
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)

        self.overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        self.overlay.fill((0, 0, 0))

        self.droite_field = pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 - 30, 90, 50)
        self.droite_assign = "right"
        self.droite_assign_prec = self.droite_assign

        self.gauche_field = pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 + 30, 90, 50)
        self.gauche_assign = "left"
        self.gauche_assign_prec = self.gauche_assign

        self.sauter_field =pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 + 90, 90, 50)
        self.sauter_assign = "up"
        self.sauter_assign_prec = self.sauter_assign

        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
        self.jauge_musique = pygame.Rect(LARGEUR_ECRAN // 2 + 35, HAUTEUR_ECRAN // 2 + 0, 250, 15)
        self.jauge_general = pygame.Rect(LARGEUR_ECRAN // 2 + 35, HAUTEUR_ECRAN // 2 + 110, 250, 15)
        self.val_jauge_musique = 50 # Valeur au debut de la jauge musique
        self.val_jauge_general = 50 # Valeur au debut de la jauge musique

    def afficher_parametres(self, ecran):
        """Affiche le menu et retourne l'action choisie"""
        # fond noir
        ecran.blit(self.overlay, (0, 0))
        

        # version du jeu
        version_txt = self.font_3.render(VERSION_JEU, True, (255, 255, 255))
        ecran.blit(version_txt, (LARGEUR_ECRAN - version_txt.get_width() - 20, HAUTEUR_ECRAN - version_txt.get_height() - 20))


        # titres
        titre_txt = self.font_1.render("Paramètres", True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 220))

        volume_txt = self.font_2.render("Volumes", True, (255, 255, 255))
        ecran.blit(volume_txt, (LARGEUR_ECRAN // 2 - volume_txt.get_width() // 2 + 160, HAUTEUR_ECRAN // 2 - 120))

        configuration_txt = self.font_2.render("Configuration", True, (255, 255, 255))
        ecran.blit(configuration_txt, (LARGEUR_ECRAN // 2 - configuration_txt.get_width() // 2 - 110, HAUTEUR_ECRAN // 2 - 120))
        
        des_touches_txt = self.font_2.render("des touches", True, (255, 255, 255))
        ecran.blit(des_touches_txt, (LARGEUR_ECRAN // 2 - des_touches_txt.get_width() // 2 - 110, HAUTEUR_ECRAN // 2 - 90))


        # volume musique
        musique_txt = self.font_3.render("Musique", True, (255, 255, 255))
        ecran.blit(musique_txt, (LARGEUR_ECRAN // 2 - musique_txt.get_width() // 2 + 160, HAUTEUR_ECRAN // 2 - 40))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_musique)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_musique / 100) * self.jauge_musique.width)
        pygame.draw.rect(ecran, (0, 200, 0),(self.jauge_musique.x, self.jauge_musique.y, largeur_remplie, self.jauge_musique.height))


        # volume général
        general_txt = self.font_3.render("Effets sonores", True, (255, 255, 255))
        ecran.blit(general_txt, (LARGEUR_ECRAN // 2 - general_txt.get_width() // 2 + 160, HAUTEUR_ECRAN // 2 + 70))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_general)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_general / 100) * self.jauge_general.width)
        pygame.draw.rect(ecran, (0, 200, 0),(self.jauge_general.x, self.jauge_general.y, largeur_remplie, self.jauge_general.height))


        # configuration des touches
        # touche droite
        droite_txt = self.font_3.render("Droite", True, (255, 255, 255))
        ecran.blit(droite_txt, (LARGEUR_ECRAN // 3 - droite_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 30))
        if self.droite_assign != "":
            pygame.draw.rect(ecran, (100, 100, 100), self.droite_field)
            droite_assign_txt = self.font_3.render(self.droite_assign, True, (255, 255, 255))
            ecran.blit(droite_assign_txt, (LARGEUR_ECRAN // 2 - droite_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 - 20))
        else:
            pygame.draw.rect(ecran, (255, 0, 0), self.droite_field)


        # touche gauche
        gauche_txt = self.font_3.render("Gauche", True, (255, 255, 255))
        ecran.blit(gauche_txt, (LARGEUR_ECRAN // 3 - gauche_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 30))
        if self.gauche_assign != "":
            pygame.draw.rect(ecran, (100, 100, 100), self.gauche_field)
            gauche_assign_txt = self.font_3.render(self.gauche_assign, True, (255, 255, 255))
            ecran.blit(gauche_assign_txt, (LARGEUR_ECRAN // 2 - gauche_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 + 40))
        else:
            pygame.draw.rect(ecran, (255, 0, 0), self.gauche_field)
        
        
        # touche sauter
        sauter_txt = self.font_3.render("Sauter", True, (255, 255, 255))
        ecran.blit(sauter_txt, (LARGEUR_ECRAN // 3 - sauter_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 100))
        if self.sauter_assign !="":
            pygame.draw.rect(ecran, (100, 100, 100), self.sauter_field)
            sauter_assign_txt = self.font_3.render(self.sauter_assign, True, (255, 255, 255))
            ecran.blit(sauter_assign_txt, (LARGEUR_ECRAN // 2 - sauter_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 + 100))
        else:
            pygame.draw.rect(ecran, (255, 0, 0), self.sauter_field)
        
        
        # bouton retour
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 210))
          
        return None
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu et retourne le choix de l'utilisateur
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "quitter" ou "volume_musique_modifié" ou "volume_général_modifié" ou None
        """
        if self.droite_field != "":
            droite_assign_prec = self.droite_assign
        if self.gauche_field != "":
            gauche_assign_prec = self.gauche_assign
        if self.sauter_field != "":
            sauter_assign_prec = self.sauter_assign
            
        if self.bouton_retour.collidepoint(pos):
            if self.droite_assign == "":
                self.droite_assign = self.droite_prec
            if self.gauche_assign == "":
                self.gauche_assign = self.gauche_assign_prec
            if self.sauter_assign == "":
                self.sauter_assign = self.sauter_assign_prec
            return "quitter"
        
        if self.jauge_musique.collidepoint(pos):
            self.val_jauge_musique = int(((pos[0] - self.jauge_musique.x) / self.jauge_musique.width) * 100)
            return "volume_musique_modifié"
        if self.jauge_general.collidepoint(pos):
            self.val_jauge_general = int(((pos[0] - self.jauge_musique.x) / self.jauge_musique.width) * 100)
            return "volume_général_modifié"
        if self.droite_field.collidepoint(pos):
            self.droite_prec = self.droite_assign
            self.droite_assign = ""
        if self.gauche_field.collidepoint(pos):
            self.gauche_prec = self.gauche_assign
            self.gauche_assign = ""
        if self.sauter_field.collidepoint(pos):
            self.sauter_prec = self.sauter_assign
            self.sauter_assign = ""
        return None
