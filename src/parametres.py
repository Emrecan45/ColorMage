import pygame
import sys
import json
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, VERSION_JEU
from config_manager import ConfigManager

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self):
        # charge les touches du joueur
        self.gestionnaire_config = ConfigManager()
        self.controls = self.gestionnaire_config.obtenir_controles()

        # tailles de police
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)

        # fond noir
        self.overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        self.overlay.fill((0, 0, 0))

        # droite
        self.droite_field = pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 - 30, 90, 50)
        self.droite_assign = self.controls.get("droite", "right")

        # gauche
        self.gauche_field = pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 + 30, 90, 50)
        self.gauche_assign = self.controls.get("gauche", "left")

        # sauter
        self.sauter_field = pygame.Rect(LARGEUR_ECRAN // 3 + 100, HAUTEUR_ECRAN // 2 + 90, 90, 50)
        self.sauter_assign = self.controls.get("sauter", "up")

        # Variable pour savoir quel champ est actuellement en cours d'attribution
        self.champ_actif = None  # Peut être "droite", "gauche", "sauter" ou None

        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
        self.jauge_musique = pygame.Rect(LARGEUR_ECRAN // 2 + 35, HAUTEUR_ECRAN // 2 + 0, 250, 15)
        self.jauge_general = pygame.Rect(LARGEUR_ECRAN // 2 + 35, HAUTEUR_ECRAN // 2 + 110, 250, 15)
        self.val_jauge_musique = 50  # Valeur au debut de la jauge musique
        self.val_jauge_general = 50  # Valeur au debut de la jauge musique

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

        # ---------volume musique
        musique_txt = self.font_3.render("Musique", True, (255, 255, 255))
        ecran.blit(musique_txt, (LARGEUR_ECRAN // 2 - musique_txt.get_width() // 2 + 160, HAUTEUR_ECRAN // 2 - 40))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_musique)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_musique / 100) * self.jauge_musique.width)
        pygame.draw.rect(ecran, (0, 200, 0), (self.jauge_musique.x, self.jauge_musique.y, largeur_remplie, self.jauge_musique.height))

        # ----------volume général
        general_txt = self.font_3.render("Effets sonores", True, (255, 255, 255))
        ecran.blit(general_txt, (LARGEUR_ECRAN // 2 - general_txt.get_width() // 2 + 160, HAUTEUR_ECRAN // 2 + 70))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_general)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_general / 100) * self.jauge_general.width)
        pygame.draw.rect(ecran, (0, 200, 0), (self.jauge_general.x, self.jauge_general.y, largeur_remplie, self.jauge_general.height))

        # -----------------configuration des touches
        # ----------touche droite
        droite_txt = self.font_3.render("Droite", True, (255, 255, 255))
        ecran.blit(droite_txt, (LARGEUR_ECRAN // 3 - droite_txt.get_width() // 2, HAUTEUR_ECRAN // 2 - 30))
        # Couleur du champ selon l'état
        if self.champ_actif == "droite":
            pygame.draw.rect(ecran, (255, 0, 0), self.droite_field)
        else:
            pygame.draw.rect(ecran, (100, 100, 100), self.droite_field)
        # Texte dans le champ
        if self.champ_actif == "droite":
            droite_assign_txt = self.font_3.render("...", True, (255, 255, 255))
        else:
            droite_assign_txt = self.font_3.render(self.droite_assign, True, (255, 255, 255))
        ecran.blit(droite_assign_txt, (LARGEUR_ECRAN // 2 - droite_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 - 20))

        # ---------touche gauche
        gauche_txt = self.font_3.render("Gauche", True, (255, 255, 255))
        ecran.blit(gauche_txt, (LARGEUR_ECRAN // 3 - gauche_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 30))
        # Couleur du champ selon l'état
        if self.champ_actif == "gauche":
            pygame.draw.rect(ecran, (255, 0, 0), self.gauche_field)
        else:
            pygame.draw.rect(ecran, (100, 100, 100), self.gauche_field)
        # Texte dans le champ
        if self.champ_actif == "gauche":
            gauche_assign_txt = self.font_3.render("...", True, (255, 255, 255))
        else:
            gauche_assign_txt = self.font_3.render(self.gauche_assign, True, (255, 255, 255))
        ecran.blit(gauche_assign_txt, (LARGEUR_ECRAN // 2 - gauche_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 + 40))
        
        # --------touche sauter
        sauter_txt = self.font_3.render("Sauter", True, (255, 255, 255))
        ecran.blit(sauter_txt, (LARGEUR_ECRAN // 3 - sauter_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 100))
        # Couleur du champ selon l'état
        if self.champ_actif == "sauter":
            pygame.draw.rect(ecran, (255, 0, 0), self.sauter_field)
        else:
            pygame.draw.rect(ecran, (100, 100, 100), self.sauter_field)
        # Texte dans le champ
        if self.champ_actif == "sauter":
            sauter_assign_txt = self.font_3.render("...", True, (255, 255, 255))
        else:
            sauter_assign_txt = self.font_3.render(self.sauter_assign, True, (255, 255, 255))
        ecran.blit(sauter_assign_txt, (LARGEUR_ECRAN // 2 - sauter_assign_txt.get_width() // 2 - 55, HAUTEUR_ECRAN // 2 + 100))
        
        # -------bouton retour
        pygame.draw.rect(ecran, (70, 70, 70), self.bouton_retour)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (LARGEUR_ECRAN // 2 - retour_txt.get_width() // 2, HAUTEUR_ECRAN // 2 + 210))
          
        return None

    def sauvegarder_controles(self):
        """Sauvegarde les touches saisies dans le fichier JSON"""
        self.controls["droite"] = self.droite_assign
        self.controls["gauche"] = self.gauche_assign
        self.controls["sauter"] = self.sauter_assign
        self.gestionnaire_config.sauvegarder_controles(self.controls)

    def gerer_events(self, evenement):
        """Gère les événements quand on est dans le menu paramètres"""
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            # Gestion des clics sur les champs de touches
            if self.droite_field.collidepoint(evenement.pos):
                self.champ_actif = "droite"
                return None
            elif self.gauche_field.collidepoint(evenement.pos):
                self.champ_actif = "gauche"
                return None
            elif self.sauter_field.collidepoint(evenement.pos):
                self.champ_actif = "sauter"
                return None
            elif self.bouton_retour.collidepoint(evenement.pos):
                self.sauvegarder_controles()
                self.champ_actif = None
                return "quitter"
            else:
                self.champ_actif = None

            # Gestion des jauges de volume
            if self.jauge_musique.collidepoint(evenement.pos):
                self.val_jauge_musique = min(100, max(0, (evenement.pos[0] - self.jauge_musique.x) / self.jauge_musique.width * 100))
            if self.jauge_general.collidepoint(evenement.pos):
                self.val_jauge_general = min(100, max(0, (evenement.pos[0] - self.jauge_general.x) / self.jauge_general.width * 100))

        elif evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                self.champ_actif = None
            elif self.champ_actif:
                nouvelle_touche = pygame.key.name(evenement.key)

                # On vide l'ancienne assignation si elle existe
                if nouvelle_touche == self.droite_assign:
                    self.droite_assign = ""
                if nouvelle_touche == self.gauche_assign:
                    self.gauche_assign = ""
                if nouvelle_touche == self.sauter_assign:
                    self.sauter_assign = ""

                # On assigne la nouvelle touche
                if self.champ_actif == "droite":
                    self.droite_assign = nouvelle_touche
                elif self.champ_actif == "gauche":
                    self.gauche_assign = nouvelle_touche
                elif self.champ_actif == "sauter":
                    self.sauter_assign = nouvelle_touche

                self.champ_actif = None
                self.sauvegarder_controles()

        return None
