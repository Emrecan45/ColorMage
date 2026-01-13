import pygame
import sys
import os
import random
import math
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, FPS, TAILLE_CELLULE
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

class Game:
    """Classe principale gérant le jeu"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Charger la configuration
        self.gestionnaire_config = ConfigManager()
        
        # Créer l'écran
        self.ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN)) 
        pygame.display.set_caption("ColorMage")
        
        # Lancer l'intro
        intro = Intro(self.ecran, self.gestionnaire_config)
        resultat_intro = intro.lancer()
        
        volumes = self.gestionnaire_config.obtenir_volumes()
        
        
        # Musique du jeu
        music_path = os.path.join("audio", "main_theme.mp3")
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
        self.joueur = Joueur(0, HAUTEUR_ECRAN - 2 * TAILLE_CELLULE, self.gestionnaire_config)
        
        # Menu d'accueil
        self.menu = Menu()
        
        # Pause
        self.pause = Pause()
        
        # Parametres
        self.parametres = Parametres(self.joueur, self.gestionnaire_config)
        
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
        
        # Son de portail spawn
        self.son_portail = pygame.mixer.Sound(os.path.join("audio", "select.mp3"))
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_portail.set_volume(volumes.get("effets", 50) / 100)
        
        # Timer global pour les animations
        self.temps_global = 0
    
    def gerer_evenements(self):
        """Gère les événements pygame"""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False

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
                        self.chrono.pause()
                        
                        self.pause.son_select.play()
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                        
                        # Reprendre le chronomètre
                        if action == "continuer":
                            self.chrono.reprendre()
                        elif action == "recommencer":
                            # Déclencher l'animation de portail d'entrée
                            self.portail_entree_actif = True
                            self.portail_entree_animation = 0
                            self.etat = "jeu"
                            self.joueur_visible = False
                            
                            self.niveau.reset(self.niveau_actuel, self.ecran)
                            self.joueur.reset()
                            self.joueur.maj_controles()
                            self.chrono.demarrer()
                            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                            self.chrono.definir_meilleur_temps(meilleur_temps)
                            self.est_record = False
                            self.son_portail.play()
                        elif action == "quitter":
                            self.chrono.arreter()
                            self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                            self.etat = "selection"
                    elif self.etat == "selection":
                        # Dans la sélection de niveaux, Échap agit comme le bouton retour
                        # Mais bloquer si des animations sont en cours
                        if self.menu_niveaux.mage_en_mouvement or self.menu_niveaux.teleportation_en_cours or self.menu_niveaux.transition_univers:
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
                            # Retour à la galaxie avec sons
                            self.menu_niveaux.son_select.play()
                            random.choice(self.menu_niveaux.sons_portail).play()
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
                            self.etat = "menu"
                if self.etat == "menu":
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.gerer_clic(evenement.pos)
                        if action == "jouer":
                            self.etat = "selection"
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
                            
                            # Recharger le profil (avec la tenue par défaut)
                            self.profil.recharger_donnees()
                            self.profil.tenue_actuelle = 0
                            self.profil.charger_image_mage()

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
                            self.parametres = Parametres(self.joueur, self.gestionnaire_config)
                            # Appliquer le volume de la musique
                            pygame.mixer.music.set_volume(0.5)
                            # Mettre à jour les contrôles du joueur
                            self.joueur.maj_controles()

                elif self.etat == "selection":
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        resultat = self.menu_niveaux.gerer_clic(evenement.pos)
                        if resultat == 0:
                            self.etat = "menu"
                        elif resultat is not None and resultat > 0:
                            self.lancer_niveau(resultat)

                elif self.etat == "jeu":
                    if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_p:
                        # Mettre en pause le chronomètre
                        self.chrono.pause()
                        
                        self.pause.son_select.play()
                        action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                        
                        # Reprendre le chronomètre
                        if action == "continuer":
                            self.chrono.reprendre()
                        elif action == "recommencer":
                            # Déclencher l'animation de portail d'entrée
                            self.portail_entree_actif = True
                            self.portail_entree_animation = 0
                            self.etat = "jeu"
                            self.joueur_visible = False
                            
                            self.niveau.reset(self.niveau_actuel, self.ecran)
                            self.joueur.reset()
                            self.joueur.maj_controles()
                            self.chrono.demarrer()
                            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                            self.chrono.definir_meilleur_temps(meilleur_temps)
                            self.est_record = False
                            self.son_portail.play()
                        elif action == "quitter":
                            self.chrono.arreter()
                            self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                            self.etat = "selection"
                    
                    # Gérer le clic sur le bouton pause
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        if self.pause.bouton_rect.collidepoint(evenement.pos):
                            # Mettre en pause le chronomètre
                            self.chrono.pause()
                            
                            self.pause.son_select.play()
                            action = self.pause.afficher_pause(self.ecran, self.joueur, self.niveau, self.niveau_actuel, self.chrono, draw_background=self.dessiner_fond_niveau)
                            
                            # Reprendre le chronomètre
                            if action == "continuer":
                                self.chrono.reprendre()
                            elif action == "recommencer":
                                # Déclencher l'animation de portail d'entrée
                                self.portail_entree_actif = True
                                self.portail_entree_animation = 0
                                self.etat = "jeu"
                                self.joueur_visible = False
                                
                                self.niveau.reset(self.niveau_actuel, self.ecran)
                                self.joueur.reset()
                                self.joueur.maj_controles()
                                self.chrono.demarrer()
                                meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
                                self.chrono.definir_meilleur_temps(meilleur_temps)
                                self.est_record = False
                                self.son_portail.play()
                            elif action == "quitter":
                                self.chrono.arreter()
                                self.menu_niveaux.preparer_retour_niveau(self.niveau_actuel)
                                self.etat = "selection"

    def lancer_niveau(self, numero):
        """Lance un niveau avec l'animation de portail"""
        self.joueur.reset()
        self.niveau_actuel = numero
        self.niveau.reset(numero, self.ecran)
        self.joueur.maj_controles()
        self.niveau.charger_niveau(numero, self.ecran)
        self.joueur.reset()
        self.joueur.maj_controles()
        # Démarrer le chronomètre et charger le meilleur temps
        self.chrono.demarrer()
        meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(numero)
        self.chrono.definir_meilleur_temps(meilleur_temps)
        self.est_record = False
        # Activer l'animation de portail d'entrée
        self.portail_entree_actif = True
        self.portail_entree_animation = 0
        self.joueur_visible = False
        self.etat = "jeu"
    
    def traiter_action_popup(self, action):
        """Traite l'action sélectionnée dans un popup"""
        if action == "suivant":
            self.niveau_actuel += 1
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset()
            self.joueur.maj_controles()
            self.chrono.demarrer()
            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
            self.chrono.definir_meilleur_temps(meilleur_temps)
            self.est_record = False
            # Activer l'animation de portail d'entrée
            self.portail_entree_actif = True
            self.portail_entree_animation = 0
            self.joueur_visible = False
            self.son_portail.play()
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
            self.menu_niveaux.etat_menu = "galaxie"
            self.menu_niveaux.zoom_en_cours = True
            self.menu_niveaux.zoom_direction = 1
            self.menu_niveaux.zoom_animation = 0
            self.etat = "selection"
        elif action == "univers_suivant":
            # Aller à l'univers suivant avec animation de swipe
            self.niveau_actuel += 1
            # Calculer le nouvel univers
            niveaux_par_univers = self.menu_niveaux.nombre_planetes_par_univers * self.menu_niveaux.niveaux_par_planete
            nouvel_univers = (self.niveau_actuel - 1) // niveaux_par_univers
            
            # Revenir à la vue galaxie de l'univers précédent
            self.menu_niveaux.etat_menu = "galaxie"
            # Démarrer l'animation de swipe vers le nouvel univers
            self.menu_niveaux.changer_univers(1)  # +1 pour aller vers la droite
            self.etat = "selection"
        elif action == "rejouer":
            self.niveau.reset(self.niveau_actuel, self.ecran)
            self.joueur.reset()
            self.joueur.maj_controles()
            self.chrono.demarrer()
            meilleur_temps = self.gestionnaire_config.obtenir_meilleur_temps(self.niveau_actuel)
            self.chrono.definir_meilleur_temps(meilleur_temps)
            # Activer l'animation de portail d'entrée
            self.portail_entree_actif = True
            self.portail_entree_animation = 0
            self.joueur_visible = False
            self.son_portail.play()
            self.est_record = False
            self.joueur_visible = True
            self.portail_entree_actif = False
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
                self.joueur_visible = False
            elif self.portail_sortie_animation >= 60:
                # Fin de l'animation, montrer le popup de victoire
                self.portail_sortie_actif = False
                self.popup_actif = "victoire"
                self.chrono.arreter()
                
                # Jouer le son de victoire maintenant
                self.joueur.son_victoire.play()
                
                # Sauvegarder le temps et vérifier si c'est un record
                temps_final = self.chrono.obtenir_temps()
                self.est_record = self.gestionnaire_config.maj_meilleur_temps(self.niveau_actuel, temps_final)
                
                # Débloquer le niveau suivant si c'était pas déjà le cas
                niveau_max = self.gestionnaire_config.obtenir_niveau_actuel()
                if self.niveau_actuel == niveau_max:
                    self.gestionnaire_config.maj_niveau_actuel(self.niveau_actuel + 1)
            return  # Ne pas mettre à jour le jeu pendant l'animation
            
        if self.etat == "jeu":
            touches = pygame.key.get_pressed()
            self.joueur.deplacer(touches, self.niveau)
            self.joueur.animer()
            # Stocke l'interaction du joueur
            resultat = self.joueur.interagir_avec_blocs(self.niveau)

            # Cas de téléportation (quand on touche le portail jaune)
            if resultat == "teleportation":
                # Démarrer l'animation de sortie
                self.portail_sortie_actif = True
                self.portail_sortie_animation = 0
                self.portail_sortie_x = self.joueur.x + self.joueur.largeur // 2
                self.portail_sortie_y = self.joueur.y + self.joueur.hauteur // 2

            # Cas de défaite
            elif resultat == "mort":
                self.popup_actif = "defaite"
                self.chrono.arreter()
                self.est_record = False

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
