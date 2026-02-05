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
        self.son_select = pygame.mixer.Sound(os.path.join("audio", "select.mp3"))
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
        
        # Tenues disponibles (couleur, fichier, pose en colonne/ligne)
        # Spritesheet: 4 colonnes x 3 lignes, chaque sprite = 192x196
        # pose_x = (colonne - 1) * 192, pose_y = (ligne - 1) * 196
        # offset_y = décalage pour compenser la position visuelle du mage dans le sprite
        self.tenues = [
            # Gris - 3 poses (offset positif = descendre l'image)
            {"nom": "Gris 1", "fichier": "joueur_gris.png", "pose_x": 0, "pose_y": 0, "offset_y": 4},        # L1 C1
            {"nom": "Gris 2", "fichier": "joueur_gris.png", "pose_x": 576, "pose_y": 196, "offset_y": 7.5},   # L2 C4
            {"nom": "Gris 3", "fichier": "joueur_gris.png", "pose_x": 192, "pose_y": 392, "offset_y": 10},  # L3 C2
            # Vert - 3 poses
            {"nom": "Vert 1", "fichier": "joueur_vert.png", "pose_x": 0, "pose_y": 0, "offset_y": 4},       # L1 C1
            {"nom": "Vert 2", "fichier": "joueur_vert.png", "pose_x": 576, "pose_y": 196, "offset_y": 7.5},  # L2 C4
            {"nom": "Vert 3", "fichier": "joueur_vert.png", "pose_x": 192, "pose_y": 392, "offset_y": 10}, # L3 C2
            # Bleu - 3 poses
            {"nom": "Bleu 1", "fichier": "joueur_bleu.png", "pose_x": 0, "pose_y": 0, "offset_y": 4},       # L1 C1
            {"nom": "Bleu 2", "fichier": "joueur_bleu.png", "pose_x": 576, "pose_y": 196, "offset_y": 7.5},  # L2 C4
            {"nom": "Bleu 3", "fichier": "joueur_bleu.png", "pose_x": 192, "pose_y": 392, "offset_y": 10}, # L3 C2
            # Rouge - 3 poses
            {"nom": "Rouge 1", "fichier": "joueur_rouge.png", "pose_x": 0, "pose_y": 0, "offset_y": 4},     # L1 C1
            {"nom": "Rouge 2", "fichier": "joueur_rouge.png", "pose_x": 576, "pose_y": 196, "offset_y": 7.5}, # L2 C4
            {"nom": "Rouge 3", "fichier": "joueur_rouge.png", "pose_x": 192, "pose_y": 392, "offset_y": 10}, # L3 C2
            # Sorcier - 2 poses
            {"nom": "Sorcier 1", "fichier": "ennemy.png", "pose_x": 0 * 192, "pose_y": 0 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
            {"nom": "Sorcier 2", "fichier": "ennemy.png", "pose_x": 3 * 192, "pose_y": 0 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
            # Squelette - 4 poses
            {"nom": "Squelette 1", "fichier": "ennemy.png", "pose_x": 2 * 192, "pose_y": 4 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
            {"nom": "Squelette 2", "fichier": "ennemy.png", "pose_x": 4 * 192, "pose_y": 4 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
            {"nom": "Squelette 3", "fichier": "ennemy.png", "pose_x": 0 * 192, "pose_y": 5 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
            {"nom": "Squelette 4", "fichier": "ennemy.png", "pose_x": 2 * 192, "pose_y": 5 * 192, "pose_w": 192, "pose_h": 192, "offset_y": 5},
        ]
        
        self.tenue_actuelle = self.gestionnaire_config.config.get("tenue_profil", 0)
        
        # Charger l'icône de changement
        try:
            self.icone_change = pygame.image.load("img/change.png")
            self.icone_change = pygame.transform.scale(self.icone_change, (40, 40))
        except:
            self.icone_change = None
        
        # Charger l'image du mage selon la tenue actuelle
        self.charger_image_mage()
        
        # Positions centrées
        centre_x = LARGEUR_ECRAN // 2
        
        # Layout : mage + bouton à gauche, 3 stats à droite
        # Mage = hauteur de 2 stats, Bouton = hauteur de 1 stat
        espacement = 25  # Espacement vertical plus grand
        stat_hauteur = 70
        bouton_hauteur = stat_hauteur  # Même hauteur que la 3ème stat
        mage_hauteur = 2 * stat_hauteur + espacement  # Hauteur de 2 stats + espacement entre elles
        mage_largeur = 200
        stats_largeur = 280
        
        # Position de départ (centrée horizontalement, plus bas du titre)
        gauche_x = centre_x - (mage_largeur + espacement + stats_largeur) // 2
        droite_x = gauche_x + mage_largeur + espacement
        top_y = 240  # Plus bas du titre
        
        # Zone d'affichage du mage (hauteur = 2 stats)
        self.cadre_mage = pygame.Rect(gauche_x, top_y, mage_largeur, mage_hauteur)
        
        # Bouton changement de tenue (sous le mage, même largeur, même hauteur que 3ème stat)
        self.bouton_change = pygame.Rect(gauche_x, top_y + mage_hauteur + espacement, mage_largeur, bouton_hauteur)
        
        # Champ pseudo (éditable, centré, plus espacé du titre)
        self.pseudo_rect = pygame.Rect(centre_x - 150, 140, 300, 50)
        self.edition_pseudo = False
        self.pseudo_avant_edition = ""  # Pour restaurer si vide
        self.curseur_visible = True
        self.temps_curseur = 0
        
        # Bouton reset sauvegarde de retour (aligné avec parametres)
        self.bouton_reset_save = pygame.Rect(centre_x - 125, HAUTEUR_ECRAN // 2 + 200, 250, 50)
        
        # Bouton retour en bas (aligné avec parametres)
        self.bouton_retour = pygame.Rect(centre_x - 125, HAUTEUR_ECRAN // 2 + 270, 250, 50)
        
        # Zones de stats
        self.zone_niveau_max = pygame.Rect(droite_x, top_y, stats_largeur, stat_hauteur)
        self.zone_temps_total = pygame.Rect(droite_x, top_y + stat_hauteur + espacement, stats_largeur, stat_hauteur)
        self.zone_cibles = pygame.Rect(droite_x, top_y + 2 * (stat_hauteur + espacement), stats_largeur, stat_hauteur)
    
    def charger_image_mage(self):
        """Charge l'image du mage selon la tenue actuelle"""
        try:
            tenue = self.tenues[self.tenue_actuelle]
            image_path = f"img/{tenue['fichier']}"
            self.image_mage_original = pygame.image.load(image_path)
            # Si c'est une spritesheet de joueur (fichier commençant par 'joueur_'), on découpe
            if tenue['fichier'].startswith('joueur_'):
                sprite_largeur = 192
                sprite_hauteur = 195  # Réduit de 1 pixel pour éviter de capturer la ligne suivante
                mage_surface = pygame.Surface((sprite_largeur, sprite_hauteur), pygame.SRCALPHA)
                mage_surface.blit(self.image_mage_original, (0, 0), 
                                (tenue['pose_x'], tenue['pose_y'], sprite_largeur, sprite_hauteur))
                self.image_mage = pygame.transform.scale(mage_surface, (150, 150))
            else:
                # Pour les autres fichiers (ennemis, icones...), on tente d'extraire
                # une sous-image si des coordonnées sont fournies, sinon on met l'image entière à l'échelle
                pose_w = tenue.get('pose_w')
                pose_h = tenue.get('pose_h')
                pose_x = tenue.get('pose_x', 0)
                pose_y = tenue.get('pose_y', 0)
                if pose_w and pose_h:
                    try:
                        frame_surface = pygame.Surface((pose_w, pose_h), pygame.SRCALPHA)
                        frame_surface.blit(self.image_mage_original, (0, 0), (pose_x, pose_y, pose_w, pose_h))
                        self.image_mage = pygame.transform.scale(frame_surface, (150, 150))
                    except Exception:
                        # Fallback to full image if crop fails
                        try:
                            self.image_mage = pygame.transform.scale(self.image_mage_original, (150, 150))
                        except Exception:
                            self.image_mage = self.image_mage_original
                else:
                    try:
                        self.image_mage = pygame.transform.scale(self.image_mage_original, (150, 150))
                    except Exception:
                        self.image_mage = self.image_mage_original
            # Stocker l'offset vertical pour cette pose
            self.mage_offset_y = tenue.get('offset_y', 0)
        except:
            self.image_mage = None
            self.mage_offset_y = 0
    
    def changer_tenue(self):
        """Change la tenue du mage"""
        self.tenue_actuelle = (self.tenue_actuelle + 1) % len(self.tenues)
        self.charger_image_mage()
        # Sauvegarder le choix
        self.gestionnaire_config.config["tenue_profil"] = self.tenue_actuelle
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
        temps_total_ms = sum(meilleurs_temps.values()) if meilleurs_temps else 0
        
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
        
        # Titre "Profil" (même hauteur que sélection du monde)
        titre = self.font_titre.render("Profil", True, (255, 255, 255))
        ecran.blit(titre, (LARGEUR_ECRAN // 2 - titre.get_width() // 2, 30))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Cadre du pseudo (en haut au centre, plus espacé)
        pseudo_zone = pygame.Rect(LARGEUR_ECRAN // 2 - 150, 110, 300, 50)
        if self.edition_pseudo:
            pygame.draw.rect(ecran, (80, 80, 100), pseudo_zone, border_radius=10)
            pygame.draw.rect(ecran, (255, 200, 50), pseudo_zone, 3, border_radius=10)
        else:
            pygame.draw.rect(ecran, (60, 60, 80), pseudo_zone, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, pseudo_zone, 3, border_radius=10)
        
        # Afficher le pseudo avec curseur clignotant si en édition
        texte_pseudo = self.pseudo if self.pseudo else ("" if self.edition_pseudo else "Cliquez pour éditer")
        if self.edition_pseudo and self.curseur_visible:
            texte_pseudo += "|"
        pseudo_txt = self.font_1.render(texte_pseudo, True, (255, 255, 255))
        ecran.blit(pseudo_txt, (pseudo_zone.centerx - pseudo_txt.get_width() // 2,
                               pseudo_zone.centery - pseudo_txt.get_height() // 2))
        self.pseudo_rect = pseudo_zone
        
        # Cadre du mage (à gauche) - juste la bordure, fond transparent
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.cadre_mage, 3, border_radius=10)
        
        if self.image_mage:
            mage_x = self.cadre_mage.centerx - self.image_mage.get_width() // 2
            # Positionner le mage au bas du cadre (posé sur la bordure blanche) + offset pour compenser la position dans le sprite
            mage_y = self.cadre_mage.bottom - self.image_mage.get_height() - 5 + self.mage_offset_y
            ecran.blit(self.image_mage, (mage_x, mage_y))
        
        # Bouton changement de tenue (sous le mage)
        couleur_btn_change = (100, 100, 110) if self.bouton_change.collidepoint(mouse_pos) else (80, 80, 90)
        pygame.draw.rect(ecran, couleur_btn_change, self.bouton_change, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_change, 3, border_radius=10)
        if self.icone_change:
            icone_x = self.bouton_change.centerx - self.icone_change.get_width() // 2
            icone_y = self.bouton_change.centery - self.icone_change.get_height() // 2
            ecran.blit(self.icone_change, (icone_x, icone_y))
        
        # Statistiques
        stats = self.calculer_statistiques()
        
        # Zone niveau maximum / planète - fond gris
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_niveau_max, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_niveau_max, 3, border_radius=10)
        niveau_txt = self.font_3.render("Progression", True, (200, 200, 200))
        niveau_y = self.zone_niveau_max.y + 10
        ecran.blit(niveau_txt, (self.zone_niveau_max.x + 15, niveau_y))
        progression_txt = self.font_2.render(f"{stats['planete']} - Niv. {stats['niveau_max']}", True, (255, 255, 255))
        progression_y = self.zone_niveau_max.y + self.zone_niveau_max.height - progression_txt.get_height() - 12 + 6
        ecran.blit(progression_txt, (self.zone_niveau_max.x + 15, progression_y))
        
        # Zone temps total (records) - fond gris
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_temps_total, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_temps_total, 3, border_radius=10)
        temps_label = self.font_3.render("Temps total (records)", True, (200, 200, 200))
        temps_label_y = self.zone_temps_total.y + 10
        ecran.blit(temps_label, (self.zone_temps_total.x + 15, temps_label_y))
        temps_txt = self.font_2.render(self.formater_temps(stats['temps_total_ms']), True, (255, 255, 255))
        temps_txt_y = self.zone_temps_total.y + self.zone_temps_total.height - temps_txt.get_height() - 12 + 6
        ecran.blit(temps_txt, (self.zone_temps_total.x + 15, temps_txt_y))
        
        # Zone pièces collectées - fond gris
        pygame.draw.rect(ecran, (80, 80, 90), self.zone_cibles, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.zone_cibles, 3, border_radius=10)
        pieces_label = self.font_3.render("Pièces", True, (200, 200, 200))
        pieces_label_y = self.zone_cibles.y + 10
        ecran.blit(pieces_label, (self.zone_cibles.x + 15, pieces_label_y))
        pieces_txt = self.font_2.render(str(stats.get('pieces_total', 0)), True, (255, 255, 255))
        pieces_txt_y = self.zone_cibles.y + self.zone_cibles.height - pieces_txt.get_height() - 12 + 6
        ecran.blit(pieces_txt, (self.zone_cibles.x + 15, pieces_txt_y))
        
        # Bouton réinitialiser sauvegarde (en rouge, au dessus de retour)
        if self.bouton_reset_save.collidepoint(mouse_pos):
            pygame.draw.rect(ecran, (150, 50, 50), self.bouton_reset_save, border_radius=10)
        else:
            pygame.draw.rect(ecran, (120, 30, 30), self.bouton_reset_save, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_reset_save, 3, border_radius=10)
        reset_txt = self.font_2.render("Réinitialiser", True, (255, 255, 255))
        ecran.blit(reset_txt, (self.bouton_reset_save.centerx - reset_txt.get_width() // 2,
                              self.bouton_reset_save.centery - reset_txt.get_height() // 2))
        
        # Bouton retour (en bas)
        couleur_retour = COULEUR_SURVOL if self.bouton_retour.collidepoint(mouse_pos) else COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur_retour, self.bouton_retour, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_retour, 3, border_radius=10)
        retour_txt = self.font_2.render("Retour", True, (255, 255, 255))
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
            
            # Clic sur le bouton changement de tenue
            if self.bouton_change.collidepoint(evenement.pos):
                self.son_select.play()
                self.changer_tenue()
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
