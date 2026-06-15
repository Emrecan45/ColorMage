import pygame
import sys
import os
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, resource_path
from core.config_manager import ConfigManager
from ui.parametres import Parametres
from ui.popup import Popup

class Pause:
    """Gère le menu de pause avec bouton et options"""
    
    def __init__(self, gestionnaire_config=None):
        self.largeur_bouton = 70
        self.hauteur_bouton = 70
        self.marge = 15
        self.image_pause = pygame.image.load(resource_path("assets/img/ui/pause.png"))
        self.image_pause = pygame.transform.scale(self.image_pause, (self.largeur_bouton, self.hauteur_bouton))
        
        # son des clics
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.son_select = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "select.wav")))
        
        # Appliquer le volume d'effets sauvegardé
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
        
        # Coordonnées du bouton pause
        self.bouton_x = LARGEUR_ECRAN - self.largeur_bouton - self.marge
        self.bouton_y = self.marge
        self.bouton_rect = pygame.Rect(self.bouton_x, self.bouton_y, self.largeur_bouton, self.hauteur_bouton)
        
        # Police
        self.font = pygame.font.Font(None, 48)
        self.font_niveau = pygame.font.Font(None, 35)  #afficher le niveau
        
        # Dimensions du popup
        self.largeur_popup = 600
        self.hauteur_popup = 520
        self.popup_rect = pygame.Rect(
            (LARGEUR_ECRAN - self.largeur_popup) // 2, 
            (HAUTEUR_ECRAN - self.hauteur_popup) // 2, 
            self.largeur_popup, 
            self.hauteur_popup
        )
        
        # Créer les boutons du menu pause
        self.bouton_continuer = pygame.Rect(0, 0, 260, 60)
        self.bouton_continuer.center = (self.popup_rect.centerx, self.popup_rect.top + 160)
        
        self.bouton_recommencer = pygame.Rect(0, 0, 260, 60)
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 250)
        self.bouton_parametres = pygame.Rect(0, 0, 260, 60)
        self.bouton_parametres.center = (self.popup_rect.centerx, self.popup_rect.top + 340)
        self.bouton_quitter = pygame.Rect(0, 0, 260, 60)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 430)
    
    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.volumes
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
    
    def dessiner_bouton(self, ecran):
        """Dessine le bouton de pause en haut à droite"""
        ecran.blit(self.image_pause, (self.bouton_x, self.bouton_y))
    
    def dessiner_popup(self, ecran, numero_niveau=None):
        """Dessine le popup de pause avec tous les boutons
        
        Args:
            ecran: Surface pygame
            numero_niveau: Numéro du niveau actuel
        """
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)
        
        # Titre
        titre_surface = self.font.render("Pause", True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 50
        ecran.blit(titre_surface, (titre_x, titre_y))
        
        # Afficher le niveau actuel sous le titre
        if numero_niveau:
            planete = ((numero_niveau - 1) // 5) + 1 
            noms_planetes = ["Terra", "Pyros", "Aquaris", "Nebula", "Cryon", "Solara", "Vortex", "Obscura"]
            if planete <= len(noms_planetes):
                nom_planete = noms_planetes[planete - 1]
            else:
                nom_planete = "Planète " + str(planete)

            niveau_texte = "Planète " + nom_planete + " - Niv. " + str(numero_niveau)
            niveau_surface = self.font_niveau.render(niveau_texte, True, (100, 100, 100))
            niveau_x = self.popup_rect.x + (self.popup_rect.width - niveau_surface.get_width()) // 2
            niveau_y = self.popup_rect.y + 100
            ecran.blit(niveau_surface, (niveau_x, niveau_y))

        # Liste des boutons avec leurs textes
        boutons = [
            (self.bouton_continuer, "Continuer"),
            (self.bouton_recommencer, "Recommencer"),
            (self.bouton_parametres, "Paramètres"),
            (self.bouton_quitter, "Quitter")
        ]
        
        # Dessiner les boutons
        for rect, texte in boutons:
            # Effet de survol
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, (200, 200, 200), rect, border_radius=10)
            else:
                pygame.draw.rect(ecran, (230, 230, 230), rect, border_radius=10)
            
            # Bordure
            pygame.draw.rect(ecran, (0, 0, 0), rect, 3, border_radius=10)
            
            # Texte du bouton
            texte_surface = self.font.render(texte, True, (0, 0, 0))
            texte_x = rect.x + (rect.width - texte_surface.get_width()) // 2
            texte_y = rect.y + (rect.height - texte_surface.get_height()) // 2
            ecran.blit(texte_surface, (texte_x, texte_y))
    
    def gerer_clic(self, pos):
        """Gère les clics de souris sur le menu pause
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "continuer", "recommencer", "quitter" ou None
        """
        if self.bouton_continuer.collidepoint(pos):
            return "continuer"
        elif self.bouton_recommencer.collidepoint(pos):
            return "recommencer"
        elif self.bouton_parametres.collidepoint(pos):
            return "parametres"
        elif self.bouton_quitter.collidepoint(pos):
            return "quitter"
        return None
    
    def afficher_pause(self, ecran, joueur, niveau, numero_niveau, chrono=None, draw_background=None, alerte=None):
        """Affiche le menu de pause avec options
        
        Args:
            ecran: Surface pygame pour l'affichage
            joueur: Instance du joueur
            niveau: Instance du niveau
            numero_niveau: Numéro du niveau actuel
            chrono: chronomètre
            alerte: instance Alerte à afficher par-dessus
        
        Returns:
            str: "continuer", "recommencer", ou "quitter"
        """
        en_pause = True
        action = "continuer"
        self.maj_volume()
        
        while en_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = self.gerer_clic(event.pos)
                    self.maj_volume()
                    if action == "parametres":
                        self.son_select.play()
                        game_ref = self.game
                        if game_ref is not None:
                            cm = game_ref.gestionnaire_config
                        else:
                            cm = self.gestionnaire_config
                        param = Parametres(joueur, cm, niveau, game_ref, depuis_partie=True)
                        popup = Popup()
                        en_params = True
                        while en_params:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                resultat = param.gerer_events(ev)
                                if resultat == "quitter":
                                    en_params = False
                                    break
                                elif resultat == "demander_reset_param":
                                    resultat_popup = popup.afficher_popup_confirmation_reset(ecran, param, "parametres", alerte=alerte)
                                    if resultat_popup == "confirmer":
                                        self.gestionnaire_config.reinitialiser_parametres()
                                        param = Parametres(joueur, self.gestionnaire_config, niveau, game_ref, depuis_partie=True)
                                        pygame.mixer.music.set_volume(0.5)
                                        joueur.maj_controles()
                                        joueur.maj_volume_effets()
                                        niveau.maj_volume_sons()
                            draw_background(ecran)
                            niveau.dessiner(ecran, 0, update_entities=False)
                            squelettes = niveau.squelettes
                            for s in squelettes:
                                s.dessiner(ecran)
                            joueur.dessiner(ecran)
                            param.afficher_parametres(ecran)
                            if alerte:
                                alerte.dessiner(ecran)
                            pygame.display.flip()
                        if game_ref is not None:
                            game_ref.maj_volume_effets()
                            game_ref.parametres = Parametres(game_ref.joueur, game_ref.gestionnaire_config, game_ref.niveau, game_ref)
                        joueur.maj_controles()
                        joueur.maj_volume_effets()
                        niveau.maj_volume_sons()
                        self.maj_volume()
                    else:
                        if action and action != "continuer":
                            self.son_select.play()
                        if action:
                            en_pause = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.maj_volume()
                        action = "continuer"
                        en_pause = False
            
            # Redessiner le niveau et le joueur en arrière-plan
            draw_background(ecran)
            niveau.dessiner(ecran, 0, update_entities=False)
            # Dessiner les squelettes sans les mettre à jour
            squelettes = niveau.squelettes
            for s in squelettes:
                s.dessiner(ecran)
            joueur.dessiner(ecran)
            chrono.dessiner(ecran)
            
            # Dessiner le popup de pause avec le numéro de niveau
            self.dessiner_popup(ecran, numero_niveau)
            if alerte:
                alerte.dessiner(ecran)
            pygame.display.flip()
        
        # Exécuter l'action demandée
        if action == "recommencer":
            niveau.reset(numero_niveau, ecran)
            joueur.reset(niveau)
        return action
