import pygame
import json
import os
import random
import math
import core.musique as musique
from core.i18n import t
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE, resource_path, EST_WEB, est_tactile
from core.son import Son
from core.assets import police, position_centree
import core.i18n as i18n
from core.config_manager import ConfigManager

class Parametres:
    """Affiche les parametres et retourne l'action choisie"""
    
    def __init__(self, joueur = None, gestionnaire_config=None, niveau=None, game=None, depuis_partie=False):
        self.joueur = joueur
        self.niveau = niveau
        self.game = game
        self.depuis_partie = depuis_partie
        # charge les touches du joueur et les volumes
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.controls = self.gestionnaire_config.obtenir_controles()
        self.volumes = self.gestionnaire_config.volumes
        
        # son des clics
        self.son_select = Son(resource_path(os.path.join("assets/audio", "select.wav")))
        volumes = self.gestionnaire_config.volumes
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
        
        # tailles de police
        self.font_1 = police(80)
        self.font_2 = police(50)
        self.font_3 = police(40)
        self.font_sous_titre = police(35)
 
        # Générer les étoiles
        self.etoiles = []
        for i in range(150):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, HAUTEUR_ECRAN)
            taille = random.randint(1, 3)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            self.etoiles.append([x, y, taille, brillance, vitesse_scintillement, random.uniform(0, 2 * math.pi)])
        
        # Timer pour l'animation
        self.temps_global = 0

        # Position du bloc de contenu
        if self.depuis_partie:
            self.bloc_y = 330
        else:
            self.bloc_y = 400

        # droite
        self.droite_field = pygame.Rect(LARGEUR_ECRAN // 3 + 110, self.bloc_y - 30, 90, 50)
        self.droite_assign = self.controls.get("droite", "right")

        # gauche
        self.gauche_field = pygame.Rect(LARGEUR_ECRAN // 3 + 110, self.bloc_y + 30, 90, 50)
        self.gauche_assign = self.controls.get("gauche", "left")

        # sauter
        self.sauter_field = pygame.Rect(LARGEUR_ECRAN // 3 + 110, self.bloc_y + 90, 90, 50)
        self.sauter_assign = self.controls.get("sauter", "up")

        # tir
        self.tir_field = pygame.Rect(LARGEUR_ECRAN // 3 + 110, self.bloc_y + 150, 90, 50)
        self.tir_assign = self.controls.get("tir", "e")

        # Variable pour savoir quel champ est actuellement en cours d'attribution
        self.champ_actif = None  # Peut être "droite", "gauche", "sauter", "tir" ou None

        # Boutons exporter / importer sauvegarde
        if not self.depuis_partie:
            self.bouton_exporter = pygame.Rect(LARGEUR_ECRAN // 2 - 172, 210, 150, 60)
            self.bouton_importer = pygame.Rect(LARGEUR_ECRAN // 2 + 23, 210, 150, 60)
        else:
            self.bouton_exporter = None
            self.bouton_importer = None

        self.bouton_reset_param = pygame.Rect(LARGEUR_ECRAN // 2 - 125, 635, 250, 50)
        self.bouton_langue = pygame.Rect(LARGEUR_ECRAN // 2 + 150, self.bloc_y + 145, 160, 50)
        self.bouton_joystick = pygame.Rect(LARGEUR_ECRAN // 3 + 15, self.bloc_y + 20, 185, 50)
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, 700, 250, 50)
        self.fichier_import_en_attente = None

        self.jauge_musique = pygame.Rect(LARGEUR_ECRAN // 2 + 35, self.bloc_y, 250, 15)
        self.jauge_general = pygame.Rect(LARGEUR_ECRAN // 2 + 35, self.bloc_y + 90, 250, 15)
        
        # Charger les valeurs sauvegardées
        self.val_jauge_musique = self.volumes.get("musique", 50)
        self.val_jauge_general = self.volumes.get("effets", 50)
        
        # Variable pour savoir si on est en train de glisser une jauge
        self.jauge_active = None
    
    def dessiner_etoiles(self, ecran):
        """Dessine les étoiles scintillantes"""
        for etoile in self.etoiles:
            x, y, taille, brillance_base, vitesse, phase = etoile
            # Scintillement
            brillance = int(brillance_base * (0.5 + 0.5 * math.sin(self.temps_global * vitesse + phase)))
            brillance = max(50, min(255, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (x, y), taille)

    def afficher_parametres(self, ecran):
        """Affiche le menu et retourne l'action choisie"""
        
        # Incrémenter le timer pour l'animation
        self.temps_global += 1
        
        # Fond étoilé au lieu de l'image
        ecran.fill((10, 10, 30))
        self.dessiner_etoiles(ecran)
        
        # version du jeu

        # titres
        titre_txt = self.font_1.render(t("param.titre"), True, (255, 255, 255))
        ecran.blit(titre_txt, (LARGEUR_ECRAN // 2 - titre_txt.get_width() // 2, 30))

        # Sous-titre t("param.sauvegarde")
        if not self.depuis_partie:
            sous_titre_save = self.font_sous_titre.render(t("param.sauvegarde"), True, (180, 180, 180))
            ecran.blit(sous_titre_save, (LARGEUR_ECRAN // 2 - sous_titre_save.get_width() // 2, self.bouton_exporter.y - 45))

        # Sous-titres volumes
        volume_txt = self.font_sous_titre.render(t("param.volumes"), True, (180, 180, 180))
        ecran.blit(volume_txt, (LARGEUR_ECRAN // 2 - volume_txt.get_width() // 2 + 160, self.bloc_y - 86))

        configuration_txt = self.font_sous_titre.render(t("param.config"), True, (180, 180, 180))
        ecran.blit(configuration_txt, (LARGEUR_ECRAN // 2 - configuration_txt.get_width() // 2 - 110, self.bloc_y - 100))
    
        des_touches_txt = self.font_sous_titre.render(t("param.touches"), True, (180, 180, 180))
        ecran.blit(des_touches_txt, (LARGEUR_ECRAN // 2 - des_touches_txt.get_width() // 2 - 110, self.bloc_y - 72))

        # ---------volume musique
        musique_txt = self.font_3.render(t("param.musique"), True, (255, 255, 255))
        ecran.blit(musique_txt, (LARGEUR_ECRAN // 2 - musique_txt.get_width() // 2 + 160, self.bloc_y - 30))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_musique)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_musique / 100) * self.jauge_musique.width)
        pygame.draw.rect(ecran, (0, 200, 0), (self.jauge_musique.x, self.jauge_musique.y, largeur_remplie, self.jauge_musique.height))

        # ----------volume général
        general_txt = self.font_3.render(t("param.sfx"), True, (255, 255, 255))
        ecran.blit(general_txt, (LARGEUR_ECRAN // 2 - general_txt.get_width() // 2 + 160, self.bloc_y + 60))
        pygame.draw.rect(ecran, (100, 100, 100), self.jauge_general)
        # remplissage de la jauge
        largeur_remplie = int((self.val_jauge_general / 100) * self.jauge_general.width)
        pygame.draw.rect(ecran, (0, 200, 0), (self.jauge_general.x, self.jauge_general.y, largeur_remplie, self.jauge_general.height))

        # -----------------configuration des touches
        
        
        if not est_tactile():
            # ----------touche droite
            droite_txt = self.font_3.render(t("param.droite"), True, (255, 255, 255))
            ecran.blit(droite_txt, (LARGEUR_ECRAN // 3 + 20 - droite_txt.get_width() // 2, self.bloc_y - 30))
            # Couleur du champ selon l'état
            if self.champ_actif == "droite":
                pygame.draw.rect(ecran, (255, 0, 0), self.droite_field, border_radius=5)
            else:
                if self.droite_field.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(ecran, COULEUR_SURVOL, self.droite_field, border_radius=5)
                else:
                    pygame.draw.rect(ecran, COULEUR_BOUTON, self.droite_field, border_radius=5)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.droite_field, 3, border_radius=5)
            # Texte dans le champ
            if self.champ_actif == "droite":
                droite_assign_txt = self.font_3.render("...", True, (255, 255, 255))
            else:
                droite_assign_txt = self.font_3.render(self.droite_assign, True, (255, 255, 255))
            ecran.blit(droite_assign_txt, position_centree(droite_assign_txt, self.font_3,
                                                           self.droite_field.centerx, self.droite_field.centery))

            # ---------touche gauche
            gauche_txt = self.font_3.render(t("param.gauche"), True, (255, 255, 255))
            ecran.blit(gauche_txt, (LARGEUR_ECRAN // 3 + 20 - gauche_txt.get_width() // 2, self.bloc_y + 30))
            # Couleur du champ selon l'état
            if self.champ_actif == "gauche":
                pygame.draw.rect(ecran, (255, 0, 0), self.gauche_field, border_radius=5)
            else:
                if self.gauche_field.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(ecran, COULEUR_SURVOL, self.gauche_field, border_radius=5)
                else:
                    pygame.draw.rect(ecran, COULEUR_BOUTON, self.gauche_field, border_radius=5)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.gauche_field, 3, border_radius=5)
            # Texte dans le champ
            if self.champ_actif == "gauche":
                gauche_assign_txt = self.font_3.render("...", True, (255, 255, 255))
            else:
                gauche_assign_txt = self.font_3.render(self.gauche_assign, True, (255, 255, 255))
            ecran.blit(gauche_assign_txt, position_centree(gauche_assign_txt, self.font_3,
                                                           self.gauche_field.centerx, self.gauche_field.centery))
        
            # --------touche sauter
            sauter_txt = self.font_3.render(t("param.sauter"), True, (255, 255, 255))
            ecran.blit(sauter_txt, (LARGEUR_ECRAN // 3 + 20 - sauter_txt.get_width() // 2, self.bloc_y + 100))
            # Couleur du champ selon l'état
            if self.champ_actif == "sauter":
                    pygame.draw.rect(ecran, (255, 0, 0), self.sauter_field, border_radius=5)
            else:
                if self.sauter_field.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(ecran, COULEUR_SURVOL, self.sauter_field, border_radius=5)
                else:
                    pygame.draw.rect(ecran, COULEUR_BOUTON, self.sauter_field, border_radius=5)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.sauter_field, 3, border_radius=5)
            # Texte dans le champ
            if self.champ_actif == "sauter":
                sauter_assign_txt = self.font_3.render("...", True, (255, 255, 255))
            else:
                sauter_assign_txt = self.font_3.render(self.sauter_assign, True, (255, 255, 255))
            ecran.blit(sauter_assign_txt, position_centree(sauter_assign_txt, self.font_3,
                                                           self.sauter_field.centerx, self.sauter_field.centery))

            # --------touche tir
            tir_txt = self.font_3.render(t("param.tir"), True, (255, 255, 255))
            ecran.blit(tir_txt, (LARGEUR_ECRAN // 3 + 20 - tir_txt.get_width() // 2, self.bloc_y + 160))
            if self.champ_actif == "tir":
                pygame.draw.rect(ecran, (255, 0, 0), self.tir_field, border_radius=5)
            else:
                if self.tir_field.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(ecran, COULEUR_SURVOL, self.tir_field, border_radius=5)
                else:
                    pygame.draw.rect(ecran, COULEUR_BOUTON, self.tir_field, border_radius=5)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.tir_field, 3, border_radius=5)
            if self.champ_actif == "tir":
                tir_assign_txt = self.font_3.render("...", True, (255, 255, 255))
            else:
                tir_assign_txt = self.font_3.render(self.tir_assign, True, (255, 255, 255))
            ecran.blit(tir_assign_txt, position_centree(tir_assign_txt, self.font_3,
                                                        self.tir_field.centerx, self.tir_field.centery))

        # -------boutons exporter/importer
        if not self.depuis_partie:
            # Bouton exporter
            if self.bouton_exporter.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, COULEUR_SURVOL, self.bouton_exporter, border_radius=10)
            else:
                pygame.draw.rect(ecran, COULEUR_BOUTON, self.bouton_exporter, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_exporter, 3, border_radius=10)
            export_txt = self.font_3.render(t("param.exporter"), True, (255, 255, 255))
            ecran.blit(export_txt, position_centree(export_txt, self.font_3,
                                                    self.bouton_exporter.centerx, self.bouton_exporter.centery))

            # Bouton importer
            if self.bouton_importer.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, COULEUR_SURVOL, self.bouton_importer, border_radius=10)
            else:
                pygame.draw.rect(ecran, COULEUR_BOUTON, self.bouton_importer, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_importer, 3, border_radius=10)
            import_txt = self.font_3.render(t("param.importer"), True, (255, 255, 255))
            ecran.blit(import_txt, position_centree(import_txt, self.font_3,
                                                    self.bouton_importer.centerx, self.bouton_importer.centery))

        
        # -------bouton langue
        lang_label = self.font_3.render(t("param.langue"), True, (255, 255, 255))
        ecran.blit(lang_label, (LARGEUR_ECRAN // 2 + 70 - lang_label.get_width() // 2, self.bloc_y + 160))

        if self.bouton_langue.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(ecran, COULEUR_SURVOL, self.bouton_langue, border_radius=5)
        else:
            pygame.draw.rect(ecran, COULEUR_BOUTON, self.bouton_langue, border_radius=5)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_langue, 3, border_radius=5)
        lang_txt = self.font_3.render(t("param.langue_actuelle"), True, (255, 255, 255))
        ecran.blit(lang_txt, position_centree(lang_txt, self.font_3,
                                              self.bouton_langue.centerx, self.bouton_langue.centery))

        # -------bouton joystick (tactile, mobile uniquement)
        if est_tactile():
            joystick_label = self.font_3.render(t("param.joystick"), True, (255, 255, 255))
            ecran.blit(joystick_label, (self.bouton_joystick.centerx - joystick_label.get_width() // 2, self.bouton_joystick.top - 35))
            if self.bouton_joystick.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, COULEUR_SURVOL, self.bouton_joystick, border_radius=5)
            else:
                pygame.draw.rect(ecran, COULEUR_BOUTON, self.bouton_joystick, border_radius=5)
            pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_joystick, 3, border_radius=5)
            if self.gestionnaire_config.config.get("joystick_fixe", False):
                mode_txt = t("param.joystick_fixe")
            else:
                mode_txt = t("param.joystick_dynamique")
            j_txt = self.font_3.render(mode_txt, True, (255, 255, 255))
            ecran.blit(j_txt, position_centree(j_txt, self.font_3, self.bouton_joystick.centerx, self.bouton_joystick.centery))

        # -------bouton réinitialiser
        if self.bouton_reset_param.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(ecran, (150, 50, 50), self.bouton_reset_param, border_radius=10)
        else:
            pygame.draw.rect(ecran, (120, 30, 30), self.bouton_reset_param, border_radius=10)
            
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_reset_param, 3, border_radius=10)
        reset_txt = self.font_2.render(t("param.reset"), True, (255, 255, 255))
        ecran.blit(reset_txt, position_centree(reset_txt, self.font_2, self.bouton_reset_param.centerx, self.bouton_reset_param.centery))
        
        # -------bouton retour
        if self.bouton_retour.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(ecran, COULEUR_SURVOL, self.bouton_retour, border_radius=10)
        else:
            pygame.draw.rect(ecran, COULEUR_BOUTON, self.bouton_retour, border_radius=10)
            
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_retour, 3, border_radius=10)
        retour_txt = self.font_2.render(t("param.retour"), True, (255, 255, 255))
        ecran.blit(retour_txt, position_centree(retour_txt, self.font_2, self.bouton_retour.centerx, self.bouton_retour.centery))
          
        return None

    def sauvegarder_controles(self):
        """Sauvegarde les touches saisies dans le fichier JSON"""
        self.controls["droite"] = self.droite_assign
        self.controls["gauche"] = self.gauche_assign
        self.controls["sauter"] = self.sauter_assign
        self.controls["tir"] = self.tir_assign
        self.gestionnaire_config.controles = self.controls
        self.gestionnaire_config.sauvegarder_config()
    
    def maj_jauge(self, pos):
        """Met à jour la valeur d'une jauge selon la position de la souris"""
        if self.jauge_active == "musique":
            nouvelle_valeur = min(100, max(0, (pos[0] - self.jauge_musique.x) / self.jauge_musique.width * 100))
            self.val_jauge_musique = nouvelle_valeur
            self.gestionnaire_config.maj_volume("musique", nouvelle_valeur, sauvegarder=False)
            # Appliquer le volume
            musique.set_volume(nouvelle_valeur / 100)
        elif self.jauge_active == "effets":
            nouvelle_valeur = min(100, max(0, (pos[0] - self.jauge_general.x) / self.jauge_general.width * 100))
            self.val_jauge_general = nouvelle_valeur
            self.gestionnaire_config.maj_volume("effets", nouvelle_valeur, sauvegarder=False)
            # Appliquer le volume à tout les sons
            if self.joueur:
                self.joueur.maj_volume_effets()
            if self.niveau:
                self.niveau.maj_volume_sons()
            # Mettre à jour les sons
            if self.game is not None:
                self.game.maj_volume_effets()
            self.son_select.set_volume(nouvelle_valeur / 100)

    def gerer_events(self, evenement):
        """Gère les événements quand on est dans le menu paramètres"""
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            # Gestion des clics sur les champs de touches
            if not est_tactile() and self.droite_field.collidepoint(evenement.pos):
                self.son_select.play()
                self.champ_actif = "droite"
                return None
            elif not est_tactile() and self.gauche_field.collidepoint(evenement.pos):
                self.son_select.play()
                self.champ_actif = "gauche"
                return None
            elif not est_tactile() and self.sauter_field.collidepoint(evenement.pos):
                self.son_select.play()
                self.champ_actif = "sauter"
                return None
            elif not est_tactile() and self.tir_field.collidepoint(evenement.pos):
                self.son_select.play()
                self.champ_actif = "tir"
                return None
            elif self.bouton_retour.collidepoint(evenement.pos):
                self.son_select.play()
                self.sauvegarder_controles()
                self.champ_actif = None
                return "quitter"
            elif not self.depuis_partie and self.bouton_exporter.collidepoint(evenement.pos):
                self.son_select.play()
                if EST_WEB:
                    if self.game is not None:
                        self.game.alerte.afficher("alerte.non_supporte_web")
                else:
                    self.exporter_fichier()
                return None
            elif not self.depuis_partie and self.bouton_importer.collidepoint(evenement.pos):
                self.son_select.play()
                if EST_WEB:
                    if self.game is not None:
                        self.game.alerte.afficher("alerte.non_supporte_web")
                else:
                    # Ouvrir le sélecteur de fichier
                    chemin = self.choisir_fichier_import()
                    if chemin:
                        self.fichier_import_en_attente = chemin
                        return "demander_import"
                return None
            
            elif self.bouton_langue.collidepoint(evenement.pos):
                self.son_select.play()
                actuelle = self.gestionnaire_config.config.get("langue", "en")
                if actuelle == "fr":
                    nouvelle = "en"
                else:
                    nouvelle = "fr"
                self.gestionnaire_config.config["langue"] = nouvelle
                self.gestionnaire_config.sauvegarder_config()
                i18n.init(nouvelle)
            elif est_tactile() and self.bouton_joystick.collidepoint(evenement.pos):
                self.son_select.play()
                nouvelle = not self.gestionnaire_config.config.get("joystick_fixe", False)
                self.gestionnaire_config.config["joystick_fixe"] = nouvelle
                self.gestionnaire_config.sauvegarder_config()
                if self.game is not None and self.game.virtual_gamepad is not None:
                    self.game.virtual_gamepad.definir_mode(nouvelle)
            elif self.bouton_reset_param.collidepoint(evenement.pos):
                self.son_select.play()
                # Demander confirmation avant reset
                return "demander_reset_param"
            
            # Gestion des jauges de volume (début du glissement)
            elif self.jauge_musique.collidepoint(evenement.pos):
                self.jauge_active = "musique"
                self.maj_jauge(evenement.pos)
            elif self.jauge_general.collidepoint(evenement.pos):
                self.jauge_active = "effets"
                self.maj_jauge(evenement.pos)
            else:
                self.champ_actif = None
        
        elif evenement.type == pygame.MOUSEBUTTONUP and evenement.button == 1:
            # Fin du glissement
            if self.jauge_active == "effets":
                self.son_select.play()
            if self.jauge_active:
                self.gestionnaire_config.sauvegarder_config()
                self.jauge_active = None
        
        elif evenement.type == pygame.MOUSEMOTION:
            # Mise à jour pendant le glissement
            if self.jauge_active:
                self.maj_jauge(evenement.pos)

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
                if nouvelle_touche == self.tir_assign:
                    self.tir_assign = ""

                # On assigne la nouvelle touche
                if self.champ_actif == "droite":
                    self.son_select.play()
                    self.droite_assign = nouvelle_touche
                elif self.champ_actif == "gauche":
                    self.son_select.play()
                    self.gauche_assign = nouvelle_touche
                elif self.champ_actif == "sauter":
                    self.son_select.play()
                    self.sauter_assign = nouvelle_touche
                elif self.champ_actif == "tir":
                    self.son_select.play()
                    self.tir_assign = nouvelle_touche

                self.champ_actif = None
                self.sauvegarder_controles()

        return None

    def exporter_fichier(self):
        """Copie le save.json dans le dossier Téléchargements"""
        source = self.gestionnaire_config.chemin_config
        dossier_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        nom_base = "ColorMage_save"
        extension = ".json"
        destination = os.path.join(dossier_downloads, nom_base + extension)
        # Si le fichier existe deja, ajouter un numero
        compteur = 1
        while os.path.isfile(destination):
            destination = os.path.join(dossier_downloads, nom_base + " (" + str(compteur) + ")" + extension)
            compteur += 1
        with open(source, "r", encoding="utf-8") as f:
            contenu = f.read()
        with open(destination, "w", encoding="utf-8") as f:
            f.write(contenu)
        if self.game is not None:
            self.game.alerte.afficher("alerte.export_ok")

    def choisir_fichier_import(self):
        """Ouvre un sélecteur de fichier et retourne le chemin choisi"""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chemin = filedialog.askopenfilename(
            title="Choisir une sauvegarde",
            filetypes=[("Fichier JSON", "*.json")],
            initialdir=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        root.destroy()
        if chemin:
            return chemin
        return None

    def importer_fichier(self):
        """Importe la sauvegarde depuis le fichier choisi"""
        source = self.fichier_import_en_attente
        self.fichier_import_en_attente = None
        if not source or not os.path.isfile(source):
            if self.game is not None:
                self.game.alerte.afficher("alerte.fichier_introuvable")
            return
        with open(source, "r", encoding="utf-8") as f:
            contenu = f.read()
        nouvelle_config = json.loads(contenu)
        cles_requises = ["controles", "volumes", "niveau_actuel"]
        valide = True
        for cle in cles_requises:
            if cle not in nouvelle_config:
                valide = False
                break
        if not valide:
            if self.game is not None:
                self.game.alerte.afficher("alerte.fichier_invalide")
            return
        # Vérifier la signature anti triche
        if "signature" in nouvelle_config:
            if not self.gestionnaire_config.verifier_signature(nouvelle_config):
                if self.game is not None:
                    self.game.alerte.afficher("alerte.sauvegarde_corrompue")
                return
        else:
            if self.game is not None:
                self.game.alerte.afficher("alerte.sauvegarde_non_signee")
            return
        self.gestionnaire_config.sauvegarder_config(nouvelle_config)
        self.controls = self.gestionnaire_config.obtenir_controles()
        self.volumes = self.gestionnaire_config.volumes
        self.droite_assign = self.controls.get("droite", "right")
        self.gauche_assign = self.controls.get("gauche", "left")
        self.sauter_assign = self.controls.get("sauter", "up")
        self.tir_assign = self.controls.get("tir", "e")
        self.val_jauge_musique = self.volumes.get("musique", 50)
        self.val_jauge_general = self.volumes.get("effets", 50)
        musique.set_volume(self.val_jauge_musique / 100)
        return "import_ok"
