import pygame
import sys
import os
import random
import math
from datetime import datetime
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE
from config_manager import ConfigManager

class Profil:
    """Page de profil du joueur"""
    
    def __init__(self, gestionnaire_config=None):
        # Polices (mêmes que paramètres pour uniformité)
        self.font_titre = pygame.font.SysFont(None, 80)
        self.font_1 = pygame.font.SysFont(None, 50)  # Pour texte boutons
        self.font_2 = pygame.font.SysFont(None, 40)  # Pour contenu stats
        self.font_3 = pygame.font.SysFont(None, 35)  # Pour labels stats
        
        # Gestionnaire de config
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        
        # Charger les données du profil
        self.pseudo = self.gestionnaire_config.obtenir_pseudo()
        
        # Son des clics
        self.son_select = pygame.mixer.Sound(os.path.join("audio", "select.wav"))
        self.maj_volume()
        
        # Générer les étoiles
        self.etoiles = []
        for _ in range(150):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, HAUTEUR_ECRAN)
            taille = random.randint(1, 3)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            self.etoiles.append([x, y, taille, brillance, vitesse_scintillement, random.uniform(0, 2 * math.pi)])
        
        self.temps_global = 0
        
        # Avatars disponibles (images dans img/avatars/)
        # niveau_associe = niveau dont l'ennemi doit être vaincu pour débloquer
        self.avatars = [
            {"nom": "Mage 1", "fichier": "mage1.png"},
            {"nom": "Mage 2", "fichier": "mage2.png"},
            {"nom": "Mage 3", "fichier": "mage3.png"},
            {"nom": "Mage 4", "fichier": "mage4.png"},
            {"nom": "Grimoire", "fichier": "grimoire.png"},
            {"nom": "Sorcier", "fichier": "sorcier.png", "niveau_associe": 3},
            {"nom": "Squelette", "fichier": "squelette.png", "niveau_associe": 4},
            {"nom": "Slime Vert", "fichier": "slime_vert.png", "niveau_associe": 5},
            {"nom": "Slime Violet", "fichier": "slime_violet.png", "niveau_associe": 5},
        ]
        
        self.avatar_actuel = self.gestionnaire_config.config.get("avatar_profil", 0)
        for idx in range(len(self.avatars)):
            if self.avatar_est_debloque(idx):
                self.avatar_actuel = idx
                break
        
        # Charger l'icône de changement
        self.icone_change = pygame.image.load("img/change.png")
        self.icone_change = pygame.transform.scale(self.icone_change, (40, 40))
        
        # Positions centrées
        centre_x = LARGEUR_ECRAN // 2
        
        espacement = 25
        stat_hauteur = 70
        bouton_hauteur = 50
        avatar_taille = 200
        stats_largeur = 280
        
        # Position de départ
        gauche_x = centre_x - (avatar_taille + espacement + stats_largeur) // 2
        droite_x = gauche_x + avatar_taille + espacement
        top_y = 280
        
        # Zone d'affichage de l'avatar
        self.cadre_avatar = pygame.Rect(gauche_x, top_y, avatar_taille, avatar_taille)
        
        # Bouton changement d'avatar
        self.bouton_change = pygame.Rect(gauche_x, top_y + avatar_taille + espacement, avatar_taille, bouton_hauteur)
        
        # Charger l'avatar actuel
        self.charger_avatar()
        
        # Champ pseudo
        self.pseudo_rect = pygame.Rect(centre_x - 150, 140, 300, 50)
        self.edition_pseudo = False
        self.pseudo_avant_edition = ""  # Pour restaurer si vide
        self.curseur_visible = True
        self.temps_curseur = 0
        
        # Bouton reset sauvegarde de retour
        self.bouton_reset_save = pygame.Rect(centre_x - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
        
        # Bouton retour en bas
        self.bouton_retour = pygame.Rect(centre_x - 125, HAUTEUR_ECRAN // 2 + 270, 250, 50)
        
        # Zones de stats
        hauteur_totale = avatar_taille + espacement + bouton_hauteur  # 275
        espacement_stats = (hauteur_totale - 3 * stat_hauteur) // 2
        self.zone_niveau_max = pygame.Rect(droite_x, top_y, stats_largeur, stat_hauteur)
        self.zone_temps_total = pygame.Rect(droite_x, top_y + stat_hauteur + espacement_stats, stats_largeur, stat_hauteur)
        self.zone_cibles = pygame.Rect(droite_x, top_y + 2 * (stat_hauteur + espacement_stats), stats_largeur, stat_hauteur)
    
    def charger_avatar(self):
        """Charge l'image d'avatar actuelle"""
        avatar = self.avatars[self.avatar_actuel]
        chemin = os.path.join("img", "avatars", avatar["fichier"])
        image = pygame.image.load(chemin)
        taille = self.cadre_avatar.width - 6
        self.image_avatar = pygame.transform.scale(image, (taille, taille))

    def avatar_est_debloque(self, index):
        """Vérifie si un avatar est débloqué"""
        avatar = self.avatars[index]
        niveau = avatar.get("niveau_associe")
        if niveau is None:
            return True
        return self.gestionnaire_config.page_vue(niveau) and self.gestionnaire_config.obtenir_meilleur_temps(niveau) is not None
    
    def changer_avatar(self):
        """Passe à l'avatar débloqué suivant"""
        s = self.avatar_actuel
        n = len(self.avatars)
        for i in range(1, n + 1):
            idx = (s + i) % n
            if self.avatar_est_debloque(idx):
                self.avatar_actuel = idx
                break
        self.charger_avatar()
        self.gestionnaire_config.config["avatar_profil"] = self.avatar_actuel
        self.gestionnaire_config.sauvegarder_config()
    
    def maj_volume(self):
        """Met à jour le volume du son"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        self.son_select.set_volume(volumes.get("effets", 50) / 100)
    
    def dessiner_etoiles(self, ecran):
        """Dessine les étoiles scintillantes"""
        for etoile in self.etoiles:
            x, y, taille, brillance_base, vitesse, phase = etoile
            brillance = int(brillance_base * (0.5 + 0.5 * math.sin(self.temps_global * vitesse + phase)))
            brillance = max(50, min(255, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (x, y), taille)
    
    def calculer_statistiques(self):
        """Calcule les statistiques du joueur"""
        config = self.gestionnaire_config.config
        
        # Niveau maximum atteint
        niveau_max = config.get("niveau_actuel", 1)
        
        # Calculer la planète correspondante
        planete = (niveau_max - 1) // 5 + 1
        noms_planetes = ["Terra", "Pyros", "Aquaris", "Nebula", "Cryon", "Solara", "Vortex", "Obscura"]
        if planete > 0:
            idx = min(planete - 1, len(noms_planetes) - 1)
            nom_planete = noms_planetes[idx]
        else:
            nom_planete = "Terra"
        
        # Meilleurs temps
        meilleurs_temps = config.get("meilleurs_temps", {})
        
        # Temps total de jeu (somme des meilleurs temps)
        if meilleurs_temps:
            temps_total_ms = sum(meilleurs_temps.values())
        else:
            temps_total_ms = 0
        
        # nombre de pièces collectées
        pieces_total = config.get("pieces_total", 0)
        return {
            "niveau_max": niveau_max,
            "planete": nom_planete,
            "temps_total_ms": temps_total_ms,
            "pieces_total": pieces_total
        }
    
    def formater_temps(self, temps_ms):
        """Formate un temps en mm:ss.ms"""
        if temps_ms == 0:
            return "00:00.000"
        minutes = temps_ms // 60000
        secondes = (temps_ms % 60000) // 1000
        ms = temps_ms % 1000
        return f"{minutes:02d}:{secondes:02d}.{ms:03d}"
    
    def formater_date(self, date_str):
        """Formate une date pour l'affichage"""
        if not date_str:
            return "Inconnue"
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%d/%m/%Y")
        except:
            return "Inconnue"
    
    def afficher_profil(self, ecran):
        """Affiche la page de profil"""
        self.maj_volume()
        self.temps_global += 1
        
        # Gestion du curseur clignotant
        self.temps_curseur += 1
        if self.temps_curseur >= 30:  # Clignote toutes les 30 frames (~0.5s)
            self.temps_curseur = 0
            self.curseur_visible = not self.curseur_visible
        
        # Fond étoilé
        ecran.fill((10, 10, 30))
        self.dessiner_etoiles(ecran)
        
        # Titre "Profil"
        titre = self.font_titre.render("Profil", True, (255, 255, 255))
        ecran.blit(titre, (LARGEUR_ECRAN // 2 - titre.get_width() // 2, 30))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Sous-titre "Pseudo"
        sous_titre_pseudo = self.font_3.render("Pseudo", True, (180, 180, 180))
        ecran.blit(sous_titre_pseudo, (LARGEUR_ECRAN // 2 - sous_titre_pseudo.get_width() // 2, 130))
        
        # Cadre du pseudo
        pseudo_zone = pygame.Rect(LARGEUR_ECRAN // 2 - 150, 155, 300, 50)
        if self.edition_pseudo:
            pygame.draw.rect(ecran, (80, 80, 100), pseudo_zone, border_radius=10)
            pygame.draw.rect(ecran, (255, 200, 50), pseudo_zone, 3, border_radius=10)
        else:
            pygame.draw.rect(ecran, (60, 60, 80), pseudo_zone, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, pseudo_zone, 3, border_radius=10)
        
        # Afficher le pseudo avec curseur clignotant si en édition
        if self.pseudo:
            texte_pseudo = self.pseudo
        elif self.edition_pseudo:
            texte_pseudo = ""
        else:
            texte_pseudo = "Cliquez pour éditer"
        if self.edition_pseudo and self.curseur_visible:
            texte_pseudo += "|"
        pseudo_txt = self.font_1.render(texte_pseudo, True, (255, 255, 255))
        ecran.blit(pseudo_txt, (pseudo_zone.centerx - pseudo_txt.get_width() // 2,
                               pseudo_zone.centery - pseudo_txt.get_height() // 2))
        self.pseudo_rect = pseudo_zone
        
        # Sous-titre "Avatar"
        sous_titre_avatar = self.font_3.render("Avatar", True, (180, 180, 180))
        ecran.blit(sous_titre_avatar, (self.cadre_avatar.centerx - sous_titre_avatar.get_width() // 2, self.cadre_avatar.y - 25))
        
        # Cadre de l'avatar
        avatar_x = self.cadre_avatar.x + 3
        avatar_y = self.cadre_avatar.y + 3
        ecran.blit(self.image_avatar, (avatar_x, avatar_y))
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.cadre_avatar, 3, border_radius=10)
        
        # Bouton changement d'avatar
        if self.bouton_change.collidepoint(mouse_pos):
            couleur_btn_change = (100, 100, 110)
        else:
            couleur_btn_change = (80, 80, 90)
        pygame.draw.rect(ecran, couleur_btn_change, self.bouton_change, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_change, 3, border_radius=10)
        if self.icone_change:
            icone_x = self.bouton_change.centerx - self.icone_change.get_width() // 2
            icone_y = self.bouton_change.centery - self.icone_change.get_height() // 2
            ecran.blit(self.icone_change, (icone_x, icone_y))
        
        # Statistiques
        stats = self.calculer_statistiques()
        
        # Sous-titre "Statistiques"
        sous_titre_stats = self.font_3.render("Statistiques", True, (180, 180, 180))
        ecran.blit(sous_titre_stats, (self.zone_niveau_max.centerx - sous_titre_stats.get_width() // 2, self.zone_niveau_max.y - 25))
        
        # Zone niveau maximum / planète
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_niveau_max, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_niveau_max, 3, border_radius=10)
        niveau_txt = self.font_3.render("Progression", True, (200, 200, 200))
        niveau_y = self.zone_niveau_max.y + 10
        ecran.blit(niveau_txt, (self.zone_niveau_max.x + 15, niveau_y))
        progression_txt = self.font_2.render(f"{stats['planete']} - Niv. {stats['niveau_max']}", True, (255, 255, 255))
        progression_y = self.zone_niveau_max.y + self.zone_niveau_max.height - progression_txt.get_height() - 12 + 6
        ecran.blit(progression_txt, (self.zone_niveau_max.x + 15, progression_y))
        
        # Zone temps total (records)
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_temps_total, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_temps_total, 3, border_radius=10)
        temps_label = self.font_3.render("Temps total (records)", True, (200, 200, 200))
        temps_label_y = self.zone_temps_total.y + 10
        ecran.blit(temps_label, (self.zone_temps_total.x + 15, temps_label_y))
        temps_txt = self.font_2.render(self.formater_temps(stats['temps_total_ms']), True, (255, 255, 255))
        temps_txt_y = self.zone_temps_total.y + self.zone_temps_total.height - temps_txt.get_height() - 12 + 6
        ecran.blit(temps_txt, (self.zone_temps_total.x + 15, temps_txt_y))
        
        # Zone pièces collectées
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_cibles, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_cibles, 3, border_radius=10)
        pieces_label = self.font_3.render("Pièces", True, (200, 200, 200))
        pieces_label_y = self.zone_cibles.y + 10
        ecran.blit(pieces_label, (self.zone_cibles.x + 15, pieces_label_y))
        pieces_txt = self.font_2.render(str(stats.get('pieces_total', 0)), True, (255, 255, 255))
        pieces_txt_y = self.zone_cibles.y + self.zone_cibles.height - pieces_txt.get_height() - 12 + 6
        ecran.blit(pieces_txt, (self.zone_cibles.x + 15, pieces_txt_y))
        
        # Bouton réinitialiser sauvegarde
        if self.bouton_reset_save.collidepoint(mouse_pos):
            pygame.draw.rect(ecran, (150, 50, 50), self.bouton_reset_save, border_radius=10)
        else:
            pygame.draw.rect(ecran, (120, 30, 30), self.bouton_reset_save, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_reset_save, 3, border_radius=10)
        reset_txt = self.font_1.render("Réinitialiser", True, (255, 255, 255))
        ecran.blit(reset_txt, (self.bouton_reset_save.centerx - reset_txt.get_width() // 2,
                              self.bouton_reset_save.centery - reset_txt.get_height() // 2))
        
        # Bouton retour
        if self.bouton_retour.collidepoint(mouse_pos):
            couleur_retour = COULEUR_SURVOL
        else:
            couleur_retour = COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur_retour, self.bouton_retour, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_retour, 3, border_radius=10)
        retour_txt = self.font_1.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (self.bouton_retour.centerx - retour_txt.get_width() // 2,
                               self.bouton_retour.centery - retour_txt.get_height() // 2))
        
        return None
    
    def gerer_events(self, evenement):
        """Gère les événements de la page profil"""
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            # Clic sur le bouton retour
            if self.bouton_retour.collidepoint(evenement.pos):
                self.son_select.play()
                self.edition_pseudo = False
                return "quitter"
            
            # Clic sur le pseudo pour l'éditer
            if self.pseudo_rect.collidepoint(evenement.pos):
                self.son_select.play()
                self.pseudo_avant_edition = self.pseudo  # Sauvegarder avant édition
                self.edition_pseudo = True
                return None
            
            # Clic sur le bouton reset
            if self.bouton_reset_save.collidepoint(evenement.pos):
                self.son_select.play()
                self.edition_pseudo = False
                # Recharger le pseudo depuis la config pour annuler toute modification en cours
                self.pseudo = self.gestionnaire_config.obtenir_pseudo()
                return "reset_save"
            
            # Clic sur le bouton changement d'avatar
            if self.bouton_change.collidepoint(evenement.pos):
                self.son_select.play()
                self.changer_avatar()
                return None
            
            # Clic ailleurs = désactiver l'édition du pseudo
            if self.edition_pseudo:
                self.edition_pseudo = False
                # Si le pseudo est vide, restaurer l'ancien
                if not self.pseudo.strip():
                    self.pseudo = self.pseudo_avant_edition
                self.gestionnaire_config.sauvegarder_pseudo(self.pseudo)
        
        # Gestion de la saisie du pseudo
        if evenement.type == pygame.KEYDOWN and self.edition_pseudo:
            if evenement.key == pygame.K_RETURN:
                self.edition_pseudo = False
                # Si le pseudo est vide, restaurer l'ancien
                if not self.pseudo.strip():
                    self.pseudo = self.pseudo_avant_edition
                self.gestionnaire_config.sauvegarder_pseudo(self.pseudo)
            elif evenement.key == pygame.K_ESCAPE:
                # Échap annule les modifications
                self.edition_pseudo = False
                self.pseudo = self.pseudo_avant_edition
            elif evenement.key == pygame.K_BACKSPACE:
                self.pseudo = self.pseudo[:-1]
            else:
                # Ajouter le caractère si c'est un caractère imprimable et pas trop long
                if len(self.pseudo) < 15 and evenement.unicode.isprintable():
                    self.pseudo += evenement.unicode
        
        return None
    
    def recharger_donnees(self):
        """Recharge les données du profil depuis la config"""
        self.pseudo = self.gestionnaire_config.obtenir_pseudo()
        if not self.avatar_est_debloque(self.avatar_actuel):
            for idx in range(len(self.avatars)):
                if self.avatar_est_debloque(idx):
                    self.avatar_actuel = idx
                    break
            self.gestionnaire_config.config["avatar_profil"] = self.avatar_actuel
            self.gestionnaire_config.sauvegarder_config()
        self.charger_avatar()
