import pygame
import sys
import os
import random
import math
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, FPS, TAILLE_CELLULE, HAUTEUR_GRILLE, resource_path
from joueur import Joueur
from niveau import Niveau
from popup import Popup
from pause import Pause
from menu import Menu
from parametres import Parametres
from config_manager import ConfigManager
from menu_niveaux import MenuNiveaux
from chronometre import Chronometre
from profil import Profil
from intro import Intro
from alerte import Alerte

class Game:
    """Classe principale gérant le jeu"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Charger la configuration
        self.gestionnaire_config = ConfigManager()
        
        # Créer l'écran
        self.plein_ecran = False
        icone = pygame.image.load(resource_path("img/logo.ico"))
        pygame.display.set_icon(icone)
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("ColorMage")
        
        # Lancer l'intro
        intro = Intro(self.ecran, self.gestionnaire_config)
        resultat_intro = intro.lancer()
        
        volumes = self.gestionnaire_config.obtenir_volumes()
        
        
        # Musique du jeu
        music_path = resource_path(os.path.join("audio", "main_theme.ogg"))
        pygame.mixer.music.load(music_path)
        # Appliquer le volume sauvegardé (de 0 à 100 converti en 0.0 à 1.0)
        volume_musique = volumes.get("musique", 50) / 100
        pygame.mixer.music.set_volume(volume_musique)
        pygame.mixer.music.play(-1)  # (-1) = musique qui tourne a l'infini
        
        self.horloge = pygame.time.Clock()
        
        # État du jeu : "menu" ou "jeu" ou "parametres" ou "selection"
        self.etat = "menu"
        
        # Niveau
        self.niveau = Niveau()
        
        # Joueur
        self.joueur = Joueur(None, None, self.gestionnaire_config)
        
        # Menu d'accueil
        self.menu = Menu()
        
        # Pause
        self.pause = Pause()
        self.pause.game = self
        
        # Parametres
        self.parametres = Parametres(self.joueur, self.gestionnaire_config, self.niveau, self)
        
        # Profil
        self.profil = Profil(self.gestionnaire_config)
        
        self.menu_niveaux = MenuNiveaux()
        self.niveau_actuel = self.gestionnaire_config.obtenir_niveau_actuel()
        
        # Chronomètre
        self.chrono = Chronometre()
        
        self.en_cours = True
        
        # Popups
        self.popup = Popup()
        self.popup_actif = None
        self.est_record = False
        
        # Animation de portail au début du niveau
        self.portail_entree_actif = False
        self.portail_entree_animation = 0
        self.joueur_visible = False
        
        # Animation de portail de sortie
        self.portail_sortie_actif = False
        self.portail_sortie_animation = 0
        self.portail_sortie_x = 0
        self.portail_sortie_y = 0
        
        # Pièces collectées pendant le niveau en cours (sauvegardées seulement à la victoire)
        self.pieces_en_cours = []
        
        # Animation d'explosion à la mort
        self._charger_frames_explosion()
        self.explosion_actif = False
        self.explosion_frame = 0
        self.explosion_x = 0
        self.explosion_y = 0
        self.explosion_timer = 0
        self.explosion_delai = 60  # ms par frame
        
        # Timer global pour les animations
        self.temps_global = 0
        
        # Sons pour slimes et pièces
        self.son_hurt = pygame.mixer.Sound(resource_path(os.path.join("audio", "hurt.wav")))
        self.son_piece = pygame.mixer.Sound(resource_path(os.path.join("audio", "piece.wav")))

        # Son d'explosion
        self.son_explosion = pygame.mixer.Sound(resource_path(os.path.join("audio", "explosion.wav")))
        
        # Sons de pause/unpause
        self.son_pause = pygame.mixer.Sound(resource_path(os.path.join("audio", "pause.wav")))
        self.son_unpause = pygame.mixer.Sound(resource_path(os.path.join("audio", "unpause.wav")))
        
        # Alerte
        self.alerte = Alerte()

        # Vérifier si la sauvegarde a été corrompue (modifiée à la main)
        if self.gestionnaire_config.sauvegarde_corrompue:
            self.alerte.afficher("Sauvegarde corrompue, progression réinitialisée !")
            self.gestionnaire_config.sauvegarde_corrompue = False

        # Appliquer le volume des effets sonores depuis les paramètres
        volumes = self.gestionnaire_config.obtenir_volumes()
        vol_effets = volumes.get("effets", 50) / 100
        self.son_hurt.set_volume(vol_effets)
        self.son_piece.set_volume(vol_effets)
        self.son_pause.set_volume(vol_effets)
        self.son_unpause.set_volume(vol_effets)
        self.son_explosion.set_volume(vol_effets)

    def _charger_frames_explosion(self):
        """Charge les frames du spritesheet d'explosion"""
        chemin = resource_path(os.path.join("img", "explosion.png"))
        spritesheet = pygame.image.load(chemin).convert_alpha()
        frame_w, frame_h = 64, 59
        nb_frames = 9
        taille_affichage = 150
        self.explosion_frames = []
        for i in range(nb_frames):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (taille_affichage, taille_affichage))
            self.explosion_frames.append(frame)

    def _demarrer_explosion(self, x_centre, y_centre):
        """Déclenche l'explosion"""
        self.son_explosion.play()
        self.explosion_actif = True
        self.explosion_frame = 0
        self.explosion_timer = pygame.time.get_ticks()
        taille = self.explosion_frames[0].get_width()
        self.explosion_x = x_centre - taille // 2
        self.explosion_y = y_centre - taille // 2
        self.joueur_visible = False

    def maj_volume_effets(self):
        """Met à jour le volume des effets sonores depuis la config"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        vol_effets = volumes.get("effets", 50) / 100
        self.son_hurt.set_volume(vol_effets)
        self.son_piece.set_volume(vol_effets)
        self.son_pause.set_volume(vol_effets)
        self.son_unpause.set_volume(vol_effets)
        self.son_explosion.set_volume(vol_effets)
        self.niveau.maj_volume_sons()
        self.joueur.maj_volume_effets()
        self.menu.maj_volume()
        self.menu_niveaux.maj_volume()
        self.profil.maj_volume()
        self.pause.maj_volume()
        self.popup.maj_volume()

    def basculer_plein_ecran(self):
        """Bascule entre plein écran et fenêtré"""
        self.plein_ecran = not self.plein_ecran
        pygame.display.quit()
        pygame.display.init()
        if self.plein_ecran:
            self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("ColorMage")
        icone = pygame.image.load(resource_path("img/logo.ico"))
        pygame.display.set_icon(icone)
    
    def gerer_evenements(self):
        """Gère les événements pygame"""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False

            # F11 / Alt+Entrée pour basculer plein écran / fenêtré
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_F11:
                    self.basculer_plein_ecran()
                elif evenement.key == pygame.K_RETURN and (evenement.mod & pygame.KMOD_ALT):
                    self.basculer_plein_ecran()

            if evenement.type == pygame.WINDOWMAXIMIZED:
                if not self.plein_ecran:
                    self.basculer_plein_ecran()

            if self.popup_actif is not None:
                if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                    # Gérer les clics selon le type de popup
                    if self.popup_actif == "victoire":
                        action = self.popup.gerer_clic_victoire(evenement.pos, self.niveau_actuel)
                    elif self.popup_actif == "defaite":
                        action = self.popup.gerer_clic_defaite(evenement.pos)
                    else:
                        action = None
                    
                    if action:
                        self.traiter_action_popup(action)
                        self.popup_actif = None
            else:
                # Gestion globale de la touche Échap
                if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                    if self.etat == "jeu":
                        # En jeu, Échap met en pause
                        self.maj_volume_effets()
                        self.son_pause.play()
                        self.chrono.pause()
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                        
                        # Reprendre le chronomètre
                        if action == "continuer":
                            self.maj_volume_effets()
                            self.son_unpause.play()
                            self.chrono.reprendre()
                        elif action == "recommencer":
                            # Déclencher l'animation de portail d'entrée
                            self.portail_entree_actif = True
                            self.portail_entree_animation = 0
                            self.etat = "jeu"
                            self.joueur_visible = False
                            self.explosion_actif = False
                            self.explosion_frame = 0
                            self.explosion_timer = 0
                            self.popup_actif = None
                            self.son_explosion.stop()
                            self.niveau.reset(self.niveau_actuel, self.ecran)
                            self.joueur.reset(self.niveau)
                            self.joueur.maj_controles()
                            self.joueur.son_spawn.play()
                            self.chrono.demarrer()
                            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                            self.chrono.definir_meilleur_temps(meilleur_temps)
                            self.est_record = False
                        elif action == "quitter":
                            self.chrono.arreter()
                            self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                            self.etat = "selection"
                    elif self.etat == "selection":
                        # Marché : Échap retourne à la galaxie
                        if self.menu_niveaux.etat_menu == "marche":
                            self.menu_niveaux.son_select.play()
                            self.menu_niveaux.quitter_marche()
                            self.menu_niveaux.etat_menu = "galaxie"
                        # Dans la sélection de niveaux, Échap agit comme le bouton retour
                        # Mais bloquer si des animations sont en cours
                        elif self.menu_niveaux.mage_en_mouvement or self.menu_niveaux.teleportation_en_cours or self.menu_niveaux.transition_univers:
                            # Bloquer Échap pendant les animations
                            pass
                        # Si une animation de zoom est en cours, l'annuler
                        elif self.menu_niveaux.zoom_en_cours:
                            # Annuler l'animation et revenir à la galaxie
                            self.menu_niveaux.son_select.play()
                            self.menu_niveaux.zoom_en_cours = False
                            self.menu_niveaux.zoom_animation = 0
                            self.menu_niveaux.etat_menu = "galaxie"
                        elif self.menu_niveaux.etat_menu == "planete":
                            # Retour à la galaxie avec son de téléportation
                            random.choice(self.menu_niveaux.sons_teleport).play()
                            self.menu_niveaux.zoom_en_cours = True
                            self.menu_niveaux.zoom_direction = -1
                        else:
                            # Retour au menu principal
                            self.menu_niveaux.son_select.play()
                            self.etat = "menu"
                    elif self.etat in ["profil", "param"]:
                        # Dans les autres menus, Échap agit comme retour
                        if self.etat == "profil" and self.profil.edition_pseudo:
                            # Si en mode édition du pseudo, Échap annule juste l'édition (géré par profil.py)
                            # Ne pas quitter le profil
                            pass
                        else:
                            # Sinon, Échap quitte le menu avec son de clic
                            if self.etat == "profil":
                                self.profil.son_select.play()
                                self.profil.edition_pseudo = False
                            elif self.etat == "param":
                                self.parametres.son_select.play()
                                self.parametres.champ_actif = None
                            self.etat = "menu"
                if self.etat == "menu":
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.gerer_clic(evenement.pos)
                        if action == "jouer":
                            self.menu_niveaux.recharger_donnees()
                            self.etat = "selection"
                        elif action == "grimoire":
                            self.popup.afficher_grimoire_complet(self.ecran)
                        elif action == "parametres":
                            self.etat = "param"
                        elif action == "profil":
                            self.profil.recharger_donnees()
                            self.etat = "profil"
                        elif action == "quitter":
                            self.en_cours = False

                elif self.etat == "profil":
                    action = self.profil.gerer_events(evenement)
                    if action == "quitter":
                        self.etat = "menu"
                    elif action == "reset_save":
                        # Afficher le popup de confirmation
                        confirmation = self.popup.afficher_popup_confirmation_reset(self.ecran, self.profil)
                        if confirmation == "confirmer":
                            # Réinitialiser la sauvegarde (uniquement progression)
                            self.gestionnaire_config.reinitialiser_sauvegarde()
                            
                            # Recharger le menu des niveaux avec la nouvelle config
                            self.menu_niveaux = MenuNiveaux()
                            
                            # Recharger le profil (avec l'avatar par défaut)
                            self.profil.recharger_donnees()
                            self.profil.avatar_actuel = 0
                            self.profil.charger_avatar()

                elif self.etat == "param":
                    action = self.parametres.gerer_events(evenement)
                    if action == "quitter":
                        self.etat = "menu"
                    elif action == "demander_reset_param":
                        # Afficher popup de confirmation pour reset paramètres
                        resultat = self.popup.afficher_popup_confirmation_reset(self.ecran, self.parametres, "parametres")
                        if resultat == "confirmer":
                            # Reset des paramètres
                            self.gestionnaire_config.reinitialiser_parametres()
                            # Recharger les paramètres
                            self.parametres = Parametres(self.joueur, self.gestionnaire_config, self.niveau, self)
                            # Appliquer le volume de la musique
                            pygame.mixer.music.set_volume(0.5)
                            # Mettre à jour les contrôles du joueur
                            self.joueur.maj_controles()
                    elif action == "demander_import":
                        # Afficher popup de confirmation pour import
                        resultat = self.popup.afficher_popup_confirmation_reset(self.ecran, self.parametres, "import")
                        if resultat == "confirmer":
                            resultat_import = self.parametres.importer_fichier()
                            if resultat_import == "import_ok":
                                # Redémarrer le jeu
                                pygame.quit()
                                os.execv(sys.executable, [sys.executable] + sys.argv)
                        else:
                            self.parametres.fichier_import_en_attente = None

                elif self.etat == "selection":
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        resultat = self.menu_niveaux.gerer_clic(evenement.pos)
                        if resultat == 0:
                            self.etat = "menu"
                        elif resultat == "marche":
                            self.menu_niveaux.etat_menu = "marche"
                        elif resultat is not None and resultat > 0:
                            self.lancer_niveau(resultat)

                elif self.etat == "jeu":
                    if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_p:
                        # Mettre en pause le chronomètre
                        self.maj_volume_effets()
                        self.son_pause.play()
                        self.chrono.pause()
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                        
                        # Reprendre le chronomètre
                        if action == "continuer":
                            self.maj_volume_effets()
                            self.son_unpause.play()
                            self.chrono.reprendre()
                        elif action == "recommencer":
                            # Déclencher l'animation de portail d'entrée
                            self.portail_entree_actif = True
                            self.portail_entree_animation = 0
                            self.etat = "jeu"
                            self.joueur_visible = False
                            self.explosion_actif = False
                            self.explosion_frame = 0
                            self.explosion_timer = 0
                            self.popup_actif = None
                            self.son_explosion.stop()
                            self.niveau.reset(self.niveau_actuel, self.ecran)
                            self.joueur.reset(self.niveau)
                            self.joueur.maj_controles()
                            self.joueur.son_spawn.play()
                            self.chrono.demarrer()
                            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                            self.chrono.definir_meilleur_temps(meilleur_temps)
                            self.est_record = False
                        elif action == "quitter":
                            self.chrono.arreter()
                            self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                            self.etat = "selection"
                    
                    # Gérer le clic sur le bouton pause
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        if self.pause.bouton_rect.collidepoint(evenement.pos):
                            # Mettre en pause le chronomètre
                            self.maj_volume_effets()
                            self.son_pause.play()
                            self.chrono.pause()
                            
                            action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                            
                            # Reprendre le chronomètre
                            if action == "continuer":
                                self.maj_volume_effets()
                                self.son_unpause.play()
                                self.chrono.reprendre()
                            elif action == "recommencer":
                                # Déclencher l'animation de portail d'entrée
                                self.portail_entree_actif = True
                                self.portail_entree_animation = 0
                                self.etat = "jeu"
                                self.joueur_visible = False
                                self.pieces_en_cours = []
                                self.explosion_actif = False
                                self.explosion_frame = 0
                                self.explosion_timer = 0
                                self.popup_actif = None
                                self.son_explosion.stop()
                                self.niveau.reset(self.niveau_actuel, self.ecran)
                                self.joueur.reset(self.niveau)
                                self.joueur.maj_controles()
                                self.joueur.son_spawn.play()
                                self.chrono.demarrer()
                                meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                                self.chrono.definir_meilleur_temps(meilleur_temps)
                                self.est_record = False
                            elif action == "quitter":
                                self.chrono.arreter()
                                self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                                self.etat = "selection"

    def lancer_niveau(self, numero):
        """Lance un niveau avec l'animation de portail"""
        self.niveau_actuel = numero
        self.pieces_en_cours = []
        self.niveau.reset(numero, self.ecran)
        self.joueur.maj_controles()
        self.niveau.charger_niveau(numero, self.ecran)
        self.joueur.reset(self.niveau)
        self.joueur.maj_controles()
        # Démarrer le chronomètre et charger le meilleur temps
        self.chrono.demarrer()
        meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(numero)
        self.chrono.definir_meilleur_temps(meilleur_temps)
        self.est_record = False
        # Popup page du grimoire (une seule fois par progression)
        if not self.gestionnaire_config.page_vue(numero):
            self.dessiner_fond_niveau(self.ecran)
            self.niveau.dessiner(self.ecran, self.temps_global, update_entities=False)
            for piece in list(self.niveau.pieces):
                piece.dessiner(self.ecran)
            self.popup.afficher_popup_grimoire(self.ecran, numero)
            self.gestionnaire_config.marquer_page_vue(numero)
            self.chrono.demarrer()
            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(numero)
            self.chrono.definir_meilleur_temps(meilleur_temps)

        # Activer l'animation de portail d'entrée
        self.portail_entree_actif = True
        self.portail_entree_animation = 0
        self.joueur_visible = False
        # Jouer le son de spawn
        self.joueur.son_spawn.play()
        self.etat = "jeu"
    
    def traiter_action_popup(self, action):
        """Traite l'action sélectionnée dans un popup"""
        if action == "suivant":
            self.niveau_actuel += 1
            self.pieces_en_cours = []
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset(self.niveau)
            self.joueur.maj_controles()
            self.chrono.demarrer()
            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
            self.chrono.definir_meilleur_temps(meilleur_temps)
            self.est_record = False
            # Popup page du grimoire (une seule fois par progression)
            if not self.gestionnaire_config.page_vue(self.niveau_actuel):
                self.dessiner_fond_niveau(self.ecran)
                self.niveau.dessiner(self.ecran, self.temps_global, update_entities=False)
                self.popup.afficher_popup_grimoire(self.ecran, self.niveau_actuel)
                self.gestionnaire_config.marquer_page_vue(self.niveau_actuel)
                self.chrono.demarrer()
                meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                self.chrono.definir_meilleur_temps(meilleur_temps)
            # Activer l'animation de portail d'entrée
            self.portail_entree_actif = True
            self.portail_entree_animation = 0
            self.joueur_visible = False
            # Jouer le son de spawn
            self.joueur.son_spawn.play()
            self.etat = "jeu"
        elif action == "planete_suivante":
            # Aller à la planète suivante avec animation de zoom
            self.niveau_actuel += 1
            # Calculer l'univers et la planète dans cet univers
            niveaux_par_univers = self.menu_niveaux.nombre_planetes_par_univers * self.menu_niveaux.niveaux_par_planete
            univers_idx = (self.niveau_actuel - 1) // niveaux_par_univers
            niveau_dans_univers = (self.niveau_actuel - 1) % niveaux_par_univers
            nouvelle_planete = niveau_dans_univers // self.menu_niveaux.niveaux_par_planete
            
            self.menu_niveaux.univers_actuel = univers_idx
            self.menu_niveaux.camera_x = univers_idx * LARGEUR_ECRAN
            self.menu_niveaux.camera_cible_x = self.menu_niveaux.camera_x
            self.menu_niveaux.planetes = self.menu_niveaux.univers[univers_idx]["planetes"]
            self.menu_niveaux.planete_selectionnee = nouvelle_planete
            
            # Charger la musique de la nouvelle planète
            planete = self.menu_niveaux.planetes[nouvelle_planete]
            nom_planete = planete["nom"].lower()
            chemin_musique = resource_path(os.path.join("audio", nom_planete + ".ogg"))
            if os.path.exists(chemin_musique):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(chemin_musique)
                vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(-1)
            
            self.menu_niveaux.etat_menu = "galaxie"
            self.menu_niveaux.zoom_en_cours = True
            self.menu_niveaux.zoom_direction = 1
            self.menu_niveaux.zoom_animation = 0
            self.menu_niveaux.recharger_donnees()
            self.etat = "selection"
        elif action == "univers_suivant":
            # Aller à l'univers suivant avec animation de swipe
            self.niveau_actuel += 1
            # Calculer le nouvel univers
            niveaux_par_univers = self.menu_niveaux.nombre_planetes_par_univers * self.menu_niveaux.niveaux_par_planete
            nouvel_univers = (self.niveau_actuel - 1) // niveaux_par_univers
            
            # Restaurer la musique principale
            pygame.mixer.music.stop()
            pygame.mixer.music.load(resource_path(os.path.join("audio", "main_theme.ogg")))
            vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
            
            # Revenir à la vue galaxie de l'univers précédent
            self.menu_niveaux.etat_menu = "galaxie"
            # Démarrer l'animation de swipe vers le nouvel univers
            self.menu_niveaux.changer_univers(1)  # +1 pour aller vers la droite
            self.menu_niveaux.recharger_donnees()
            self.etat = "selection"
        elif action == "rejouer":
            self.pieces_en_cours = []
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset(self.niveau)
            self.joueur.maj_controles()
            self.chrono.demarrer()
            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
            self.chrono.definir_meilleur_temps(meilleur_temps)
            # Activer l'animation de portail d'entrée
            self.portail_entree_actif = True
            self.portail_entree_animation = 0
            self.joueur_visible = False
            self.est_record = False
            self.joueur.son_spawn.play()
            self.etat = "jeu"
        elif action == "quitter":
            self.chrono.arreter()
            self.est_record = False
            self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
            self.etat = "selection"
    
    def maj(self):
        """Met à jour la logique du jeu"""
        # Incrémenter le timer global
        self.temps_global += 1
        
        # Vérifier si un niveau doit être lancé depuis le menu
        if self.etat == "selection":
            niveau = self.menu_niveaux.verifier_niveau_a_lancer()
            if niveau is not None:
                self.lancer_niveau(niveau)
                return
            self.menu_niveaux.maj()
            return

        # Ne pas mettre à jour si un popup est actif
        if self.popup_actif is not None:
            return None
        
        # Animation de portail d'entrée
        if self.portail_entree_actif:
            self.portail_entree_animation += 1
            if self.portail_entree_animation >= 30:
                self.joueur_visible = True
            if self.portail_entree_animation >= 60:
                self.portail_entree_actif = False
            return  # Ne pas mettre à jour le jeu pendant l'animation
        
        # Animation de portail de sortie
        if self.portail_sortie_actif:
            self.portail_sortie_animation += 1
            if self.portail_sortie_animation == 30:
                # Le joueur disparaît dans le portail
                self.joueur.son_finish.play()
                self.joueur_visible = False
            elif self.portail_sortie_animation >= 60:
                # Fin de l'animation, montrer le popup de victoire
                self.portail_sortie_actif = False
                self.popup_actif = "victoire"
                self.chrono.arreter()
                
                # Jouer le son de victoire maintenant
                self.joueur.son_victoire.play()
                
                # Sauvegarder les pièces collectées pendant ce niveau
                for pos in self.pieces_en_cours:
                    self.gestionnaire_config.sauvegarder_piece_collectee(self.niveau_actuel, pos[0], pos[1])
                self.pieces_en_cours = []
                
                # Sauvegarder le temps et vérifier si c'est un record
                temps_final = self.chrono.obtenir_temps()
                self.est_record = self.gestionnaire_config.maj_meilleur_temps(self.niveau_actuel, temps_final)
                
                # Débloquer le niveau suivant si c'était pas déjà le cas
                niveau_max = self.gestionnaire_config.obtenir_niveau_actuel()
                if self.niveau_actuel == niveau_max:
                    self.gestionnaire_config.maj_niveau_actuel(self.niveau_actuel + 1)
                
                # Vérifier si de nouveaux avatars sont débloqués
                for avatar in self.profil.avatars:
                    niv = avatar.get("niveau_associe")
                    if niv is not None and niv == self.niveau_actuel:
                        self.alerte.afficher("Nouvel avatar disponible !")
                        break
            return  # Ne pas mettre à jour le jeu pendant l'animation
        
        # Animation d'explosion
        if self.explosion_actif:
            temps_actuel = pygame.time.get_ticks()
            if temps_actuel - self.explosion_timer >= self.explosion_delai:
                self.explosion_timer = temps_actuel
                self.explosion_frame += 1
                if self.explosion_frame >= len(self.explosion_frames):
                    self.explosion_actif = False
                    if self.etat == "jeu":
                        self.popup_actif = "defaite"
                    self.joueur.son_mort.play()
                    self.chrono.arreter()
                    self.est_record = False
            return 
            
        if self.etat == "jeu":
            touches = pygame.key.get_pressed()
            resultat = None
            resultat_deplacement = self.joueur.deplacer(touches, self.niveau)

            self.joueur.pousse_plateforme = False
            self.niveau.maj_plateformes(self.temps_global)
            rc = self.niveau.appliquer_pousse_plateforme(self.joueur)
            if rc == "mort":
                # Écrasement
                self.pieces_en_cours = []
                cx = self.joueur.x + self.joueur.largeur // 2
                cy = self.joueur.y + self.joueur.hauteur // 2
                self._demarrer_explosion(cx, cy)
                return
            if resultat_deplacement == "mort":
                resultat = "mort"
            # tomber dans le vide
            mort_vide = False
            if self.joueur.y > (HAUTEUR_GRILLE * TAILLE_CELLULE):
                mort_vide = True
                resultat = "mort"
            self.joueur.animer()
            # Stocke l'interaction du joueur
            inter_result = self.joueur.interagir_avec_blocs(self.niveau)
            if inter_result is not None:
                if inter_result == "mort":
                    resultat = "mort"
                elif resultat is None:
                    resultat = inter_result

            # Vérifier collision projectiles -> joueur
            player_hitbox = pygame.Rect(
                self.joueur.x + self.joueur.marge_x,
                self.joueur.y + self.joueur.marge_y_haut,
                self.joueur.largeur - 2 * self.joueur.marge_x,
                self.joueur.hauteur - self.joueur.marge_y_haut - self.joueur.marge_y_bas,
            )
            player_img = self.joueur.obtenir_image_courante()
            player_mask = self.joueur.obtenir_masque_courant()

            proj_iter = list(self.niveau.projectiles)
            # toucher un sorcier tue
            sorcier_list = list(self.niveau.sorciers)
            for sorcier in sorcier_list:
                sor_rect = sorcier.rect
                if player_hitbox.colliderect(sor_rect):
                    resultat = "mort"
                    break

            # toucher un squelette (fumer tue)
            squelette_list = getattr(self.niveau, 'squelettes', [])
            for squelette in list(squelette_list):
                draw_x = int(getattr(squelette, 'current_draw_x', getattr(squelette, 'x', 0)))
                draw_y = int(getattr(squelette, 'current_draw_y', getattr(squelette, 'y', 0)))
                frame_w = int(getattr(squelette, 'width', TAILLE_CELLULE * 2))
                frame_h = int(getattr(squelette, 'height', TAILLE_CELLULE * 2))
                frame_rect = pygame.Rect(draw_x, draw_y, frame_w, frame_h)
                if not player_hitbox.colliderect(frame_rect):
                    continue

                # Utiliser les masques pour la collision
                squ_mask = getattr(squelette, 'current_mask', None)
                if squ_mask is not None and player_mask is not None:
                    offset = (int(self.joueur.x - getattr(squelette, 'current_draw_x', squelette.x)),
                              int(self.joueur.y - getattr(squelette, 'current_draw_y', squelette.y)))
                    if squ_mask.overlap(player_mask, offset) is not None:
                        resultat = "mort"
                        break
                    else:
                        # pour éviter que le joueur ne meurt en touchant juste le rectangle de collision du squelette on vérifie aussi la collision par masque
                        continue
                else:
                    # si pas de masque
                    resultat = "mort"
                    break

            # Collision avec les slimes
            for slime in list(self.niveau.slimes):
                if slime.en_train_de_mourir:
                    continue
                if not player_hitbox.colliderect(slime.rect):
                    continue
                # Vérifier si le joueur tombe sur le slime (pieds du joueur au dessus du milieu du slime)
                pieds_joueur = player_hitbox.bottom
                milieu_slime = slime.rect.top + slime.rect.height // 2
                joueur_descend = self.joueur.vitesse_y > 0
                if joueur_descend and pieds_joueur <= milieu_slime + 15:
                    # Le joueur saute sur le slime
                    self.son_hurt.play()
                    slime.recevoir_degats()
                    # Rebond du joueur
                    self.joueur.vitesse_y = -17
                    self.joueur.au_sol = False
                else:
                    resultat = "mort"
                    break

            # Collision avec les pièces
            for piece in list(self.niveau.pieces):
                if not piece.alive:
                    continue
                if player_hitbox.colliderect(piece.rect):
                    self.son_piece.play()
                    piece.alive = False
                    # Stocker temporairement la piece collectee
                    cx = int(piece.x // TAILLE_CELLULE)
                    cy = int(piece.y // TAILLE_CELLULE)
                    self.pieces_en_cours.append([cx, cy])

            for proj in proj_iter:
                rect = proj.rect

                if not proj.collidable:
                    continue

                shrink_x = int(rect.width * 0.5)
                shrink_y = int(rect.height * 0.5)
                contracted_rect = rect.inflate(-shrink_x, -shrink_y)
                if not contracted_rect.colliderect(player_hitbox):
                    continue

                proj_frame_index = proj.frame_index
                proj_frames = proj.frames
                proj_masks = proj.masks

                collided = False
                if player_mask is not None and proj_masks:
                    mask_pair = proj_masks[proj_frame_index] if proj_frame_index < len(proj_masks) else (None, None)
                    if mask_pair[0] is None:
                        if proj_frames:
                            pf = proj_frames[proj_frame_index]
                            if proj.direction == -1:
                                pf = pygame.transform.flip(pf, True, False)
                            proj_mask = pygame.mask.from_surface(pf)
                        else:
                            proj_mask = None
                    else:
                        proj_mask = mask_pair[0] if proj.direction == 1 else mask_pair[1]

                    if proj_mask is not None:
                        offset = (int(self.joueur.x - proj.x), int(self.joueur.y - proj.y))
                        if proj_mask.overlap(player_mask, offset) is not None:
                            collided = True

                if not collided and rect.colliderect(player_hitbox):
                    collided = True

                if collided:
                    proj.alive = False
                    resultat = "mort"
                    break

            # Cas de téléportation (quand on touche le portail jaune)
            if resultat == "teleportation":
                # Démarrer l'animation de sortie
                self.portail_sortie_actif = True
                self.portail_sortie_animation = 0
                self.portail_sortie_x = self.joueur.x + self.joueur.largeur // 2
                self.portail_sortie_y = self.joueur.y + self.joueur.hauteur // 2
                self.joueur.son_finish.play()

            # Cas de défaite
            elif resultat == "mort":
                # Les pièces collectées pendant cette tentative sont perdues
                self.pieces_en_cours = []
                if mort_vide:
                    self.popup_actif = "defaite"
                    self.joueur.son_mort.play()
                    self.chrono.arreter()
                    self.est_record = False
                else:
                    cx = self.joueur.x + self.joueur.largeur // 2
                    cy = self.joueur.y + self.joueur.hauteur // 2
                    self._demarrer_explosion(cx, cy)

    def afficher(self):
        """Dessine tous les éléments"""
        if self.etat == "menu":
            self.menu.afficher_menu(self.ecran)
            
        elif self.etat == "selection": 
            self.menu_niveaux.afficher_selection(self.ecran)
            
        elif self.etat == "jeu":
            self.dessiner_fond_niveau(self.ecran)
            self.niveau.dessiner(self.ecran, self.temps_global)
            
            # Dessiner le portail d'entrée si actif
            if self.portail_entree_actif:
                self.dessiner_portail_jeu(self.joueur.x + self.joueur.largeur // 2, 
                                          self.joueur.y + self.joueur.hauteur // 2)
            
            # Dessiner le portail de sortie si actif
            if self.portail_sortie_actif:
                self.dessiner_portail_jeu(self.portail_sortie_x, self.portail_sortie_y, "sortie")
            
            # Dessiner le joueur seulement s'il est visible ET pas d'animation de portail ET si aucun popup n'est affiché
            if self.joueur_visible and not self.portail_entree_actif and not self.portail_sortie_actif and self.popup_actif is None:
                self.joueur.dessiner(self.ecran)
            
            # Dessiner l'explosion
            if self.explosion_actif and self.explosion_frame < len(self.explosion_frames):
                self.ecran.blit(self.explosion_frames[self.explosion_frame],
                                (self.explosion_x, self.explosion_y))
            
            if self.popup_actif is None:
                self.pause.dessiner_bouton(self.ecran)
            self.chrono.dessiner(self.ecran)
            
            # Afficher le popup s'il y en a un
            if self.popup_actif == "victoire":
                temps_final = self.chrono.obtenir_temps()
                self.popup.dessiner_popup_victoire(self.ecran, self.niveau_actuel, temps_final, self.est_record)
            elif self.popup_actif == "defaite":
                self.popup.dessiner_popup_defaite(self.ecran, self.niveau_actuel)

        elif self.etat == "param":
            self.parametres.afficher_parametres(self.ecran)
        
        elif self.etat == "profil":
            self.profil.afficher_profil(self.ecran)
        
        # Alerte par-dessus tout
        self.alerte.dessiner(self.ecran)
        
        pygame.display.flip()
    
    def dessiner_fond_niveau(self, ecran):
        """Dessine le fond du niveau basé sur la planète actuelle"""
        info_planete = self.menu_niveaux.obtenir_info_planete(self.niveau_actuel)
        couleur = info_planete.get("couleur", (100, 100, 100))
        self.niveau.dessiner_fond(ecran, couleur, self.temps_global)
    
    def dessiner_portail_jeu(self, x, y, type_portail="entree"):
        """Dessine un portail de téléportation jaune/doré dans le jeu"""
        
        # Choisir l'animation selon le type de portail
        if type_portail == "sortie":
            animation_timer = self.portail_sortie_animation
        else:
            animation_timer = self.portail_entree_animation
        
        # Effet de rotation et pulsation
        pulse = 1 + 0.2 * math.sin(animation_timer * 0.3)
        taille = 50
        rayon = int(taille * pulse)
        
        # Cercles concentriques pour l'effet de portail
        for i in range(5):
            alpha = 180 - i * 35
            r = rayon - i * (rayon // 6)
            if r > 0:
                # Couleur jaune/dorée avec variation
                teinte = 200 + int(55 * math.sin(animation_timer * 0.2 + i))
                surface = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, teinte, 50, alpha), (r + 5, r + 5), r)
                self.ecran.blit(surface, (x - r - 5, y - r - 5))
        
        # Particules tourbillonnantes
        for i in range(8):
            angle = animation_timer * 0.15 + i * (math.pi / 4)
            dist = rayon * 0.7
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            particle_size = 3 + int(2 * math.sin(animation_timer * 0.4 + i))
            pygame.draw.circle(self.ecran, (255, 255, 150), (px, py), particle_size)
        
        # Centre brillant
        pygame.draw.circle(self.ecran, (255, 255, 200), (x, y), rayon // 4)
    
    def run(self):
        """Lance la boucle principale"""
        while self.en_cours:
            self.gerer_evenements()
            self.maj()
            self.afficher()
            self.horloge.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = Game()
    jeu.run()
