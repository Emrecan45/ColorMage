import pygame
import os
import math
import random
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, NIVEAUX_DISPONIBLES, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE, resource_path
from core.config_manager import ConfigManager
from ui.profil import Profil

class MenuNiveaux:
    """Menu de sélection des niveaux avec système de planètes et univers"""

    def __init__(self, gestionnaire_config=None):
        self.font_1 = pygame.font.SysFont(None, 80)
        self.font_2 = pygame.font.SysFont(None, 50)
        self.font_3 = pygame.font.SysFont(None, 40)
        self.font_petit = pygame.font.SysFont(None, 30)
        
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.profil = Profil(self.gestionnaire_config)
        self.config = self.gestionnaire_config.charger_config()
        self.niveau_max_debloque = self.config["niveau_actuel"]
        self.pieces_total_cache = self.config.get("pieces_total", 0)
        self.niveaux_par_planete = 5
        
        # Système d'univers
        self.univers_actuel = 0
        self.univers = [
            {
                "nom": "Royaume Nord",
                "planetes": [
                    {"nom": "Terra", "couleur": (100, 180, 100), "x": LARGEUR_ECRAN // 5, "y": HAUTEUR_ECRAN // 2, "rayon": 70, "anneaux": False},
                    {"nom": "Pyros", "couleur": (200, 80, 60), "x": LARGEUR_ECRAN // 2, "y": HAUTEUR_ECRAN // 3, "rayon": 60, "anneaux": False},
                    {"nom": "Aquaris", "couleur": (60, 120, 200), "x": LARGEUR_ECRAN * 3 // 4, "y": HAUTEUR_ECRAN * 2 // 3, "rayon": 80, "anneaux": True},
                    {"nom": "Nebula", "couleur": (150, 80, 180), "x": LARGEUR_ECRAN * 4 // 5, "y": HAUTEUR_ECRAN // 4, "rayon": 55, "anneaux": False},
                ]
            },
            {
                "nom": "Royaume Sud",
                "planetes": [
                    {"nom": "Cryon", "couleur": (150, 220, 255), "x": LARGEUR_ECRAN // 4, "y": HAUTEUR_ECRAN // 3, "rayon": 65, "anneaux": False},
                    {"nom": "Solara", "couleur": (255, 180, 50), "x": LARGEUR_ECRAN // 2, "y": HAUTEUR_ECRAN * 2 // 3 - 40, "rayon": 75, "anneaux": False},
                    {"nom": "Vortex", "couleur": (180, 180, 200), "x": LARGEUR_ECRAN * 3 // 4, "y": HAUTEUR_ECRAN // 3, "rayon": 55, "anneaux": True},
                    {"nom": "Obscura", "couleur": (60, 40, 80), "x": LARGEUR_ECRAN * 4 // 5, "y": HAUTEUR_ECRAN * 3 // 4, "rayon": 70, "anneaux": False},
                ]
            }
        ]
        
        # Calculer le nombre total de niveaux et planètes
        self.nombre_planetes_par_univers = 4
        self.nombre_niveaux = len(self.univers) * self.nombre_planetes_par_univers * self.niveaux_par_planete
        
        # Référence aux planètes de l'univers actuel
        self.planetes = self.univers[self.univers_actuel]["planetes"]
        
        # Système de caméra pour le swipe entre univers
        self.camera_x = self.univers_actuel * LARGEUR_ECRAN  # Position actuelle de la caméra
        self.camera_cible_x = self.camera_x  # Position cible
        self.camera_vitesse = 0.08  # Vitesse de déplacement de la caméra
        self.transition_univers = False  # True pendant l'animation de swipe
        
        # Charger l'image du mage pour le menu
        self.image_mage = pygame.image.load(resource_path("assets/img/entities/joueur_gris.png"))
        sprite_largeur = 192
        sprite_hauteur = 196
        self.mage_sprite = self.image_mage.subsurface(pygame.Rect(0, 0, sprite_largeur, sprite_hauteur))
        self.mage_sprite = pygame.transform.scale(self.mage_sprite, (60, 60))
        self.mage_sprite_flip = pygame.transform.flip(self.mage_sprite, True, False)
        
        # Charger l'icône de pièce
        piece_sheet = pygame.image.load(resource_path("assets/img/items/piece.png"))
        piece_frame = piece_sheet.subsurface(pygame.Rect(0, 0, 16, 16))
        self.icone_piece = pygame.transform.scale(piece_frame, (48, 48))
        
        # Charger les frames de marche du mage
        self.mage_walk_frames = []
        positions_marche = [(0, 0), (2, 1), (3, 1), (0, 2)]
        for col, ligne in positions_marche:
            x_sprite = col * sprite_largeur
            y_sprite = ligne * sprite_hauteur
            sprite = self.image_mage.subsurface(pygame.Rect(x_sprite, y_sprite, sprite_largeur, sprite_hauteur))
            sprite = pygame.transform.scale(sprite, (60, 60))
            self.mage_walk_frames.append(sprite)
        
        # État du menu : "galaxie" ou "planete"
        self.etat_menu = "galaxie"
        self.planete_selectionnee = 0
        self.zoom_animation = 0  # 0 = pas de zoom, 1 = zoom complet
        self.zoom_en_cours = False
        self.zoom_direction = 0  # 1 = zoom in, -1 = zoom out
        self.vitesse_zoom = 0.04
        
        # Position du mage sur la planète
        self.mage_niveau_actuel = 1
        self.mage_x = 0
        self.mage_y = 0
        self.mage_cible_x = 0
        self.mage_cible_y = 0
        self.mage_en_mouvement = False
        self.mage_vitesse = 8 
        self.mage_direction = 1  # 1 = droite, -1 = gauche
        self.niveau_cible = None
        
        # Animation de saut
        self.mage_en_saut = False
        self.mage_saut_progression = 0
        self.mage_saut_start_x = 0
        self.mage_saut_start_y = 0
        self.mage_hauteur_saut = 80
        
        # Animation de marche
        self.mage_frame_index = 0
        self.mage_anim_timer = 0
        self.mage_anim_delay = 100
        
        # Animation du portail
        self.portail_actif = False
        self.portail_animation = 0
        self.portail_x = 0
        self.portail_y = 0
        self.mage_visible = True
        self.teleportation_en_cours = False
        self.niveau_a_lancer = None
        self.alerte = None

        # Chemin de plaques pour la marche
        self.chemin_plaques = []  # Liste des indices de plaques à parcourir
        self.plaque_courante_index = 0  # Index dans le chemin
        
        # Pour savoir si on revient d'un niveau
        self.retour_niveau = False
        self.niveau_retour = None
        
        # Flèches de navigation entre univers
        self.fleche_droite_rect = pygame.Rect(LARGEUR_ECRAN - 120, HAUTEUR_ECRAN // 2 - 40, 80, 80)
        self.fleche_gauche_rect = pygame.Rect(40, HAUTEUR_ECRAN // 2 - 40, 80, 80)
        
        # Étoiles en arrière-plan
        self.etoiles = []
        for i in range(150):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, HAUTEUR_ECRAN)
            taille = random.randint(1, 3)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            self.etoiles.append([x, y, taille, brillance, vitesse_scintillement, random.uniform(0, 2 * math.pi)])
        
        # Positions des plaques de niveaux sur la planète (vue zoomée)
        self.plaques_positions = []
        self.generer_plaques_positions()
        
        # Bouton retour aligné avec les autres pages (centré, même hauteur)
        self.bouton_retour = pygame.Rect(LARGEUR_ECRAN // 2 - 125, HAUTEUR_ECRAN // 2 + 270, 250, 50)
        
        self.image_cadenas = pygame.image.load(resource_path("assets/img/ui/cadena.png"))
        self.image_cadenas = pygame.transform.scale(self.image_cadenas, (30, 30))
    
        # son des clics
        self.son_select = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "select.wav")))
        # Son de pièce (joué lors d'un achat dans le marché)
        self.son_piece = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "piece.wav")))
        # Sons de portail (changement de couleur) pour clic sur planète
        self.sons_portail = [
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change1.wav"))),
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change2.wav"))),
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change3.wav")))
        ]
        # Sons de téléportation pour entrer/sortir d'une planète
        self.sons_teleport = []
        for i in range(1, 7):
            son = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "teleport" + str(i) + ".wav")))
            self.sons_teleport.append(son)
        self.maj_volume()
        
        # Charger l'icône du marché
        self.icone_marche = pygame.image.load(resource_path(os.path.join("assets", "img", "ui", "market.png")))
        self.icone_marche = pygame.transform.scale(self.icone_marche, (48, 48))
        
        # Bouton Marché
        self.bouton_marche = pygame.Rect(40, 25, 190, 55)
        
        # État du marché
        self.musique_marche_active = False
        self.marche_section = None
        # Catégories du marché
        self.marche_categories = [
            {"nom": "Avatars", "section": "avatars", "disponible": True},
            {"nom": "Power-ups", "section": "powerups", "disponible": True},
        ]
        self.boutons_categories = []
        # Cache des images d'avatars et de power-ups
        self.avatars_marche_cache = None
        self.powerups_marche_cache = None
        self.boutons_achats = []
        self.boutons_powerups = []
        # Achat en attente de confirmation et boutons du popup
        self.achat_en_attente = None
        self.bouton_achat_confirmer = pygame.Rect(0, 0, 200, 55)
        self.bouton_achat_confirmer.center = (LARGEUR_ECRAN // 2 - 110, HAUTEUR_ECRAN // 2 + 70)
        self.bouton_achat_annuler = pygame.Rect(0, 0, 200, 55)
        self.bouton_achat_annuler.center = (LARGEUR_ECRAN // 2 + 110, HAUTEUR_ECRAN // 2 + 70)

        # Timer global pour les animations
        self.temps_global = 0

    def construire_cache_avatars_marche(self):
        """Précharge les images d'avatars du marché."""
        taille = 80
        cache = []
        for avatar in self.profil.avatars:
            try:
                chemin = resource_path(os.path.join("assets", "img", "ui", "avatars", avatar["fichier"]))
                img = pygame.image.load(chemin).convert_alpha()
                cache.append(pygame.transform.scale(img, (taille, taille)))
            except Exception:
                cache.append(None)
        self.avatars_marche_cache = cache

    def construire_cache_powerups_marche(self):
        """Précharge les images des power-ups du marché."""
        taille = 120
        cache = []
        for powerup in self.profil.powerups:
            try:
                chemin = resource_path(os.path.join("assets", "img", "ui", powerup["fichier"]))
                img = pygame.image.load(chemin).convert_alpha()
                cache.append(pygame.transform.scale(img, (taille, taille)))
            except Exception:
                cache.append(None)
        self.powerups_marche_cache = cache

    def generer_plaques_positions(self):
        """Génère les positions des plaques de niveaux sur une planète"""
        self.plaques_positions = []
        centre_x = LARGEUR_ECRAN // 2
        centre_y = HAUTEUR_ECRAN // 2 + 50
        
        # Créer un chemin sinueux pour les plaques
        for i in range(self.niveaux_par_planete):
            x = centre_x - 250 + i * 130
            y = centre_y - abs(math.sin(i * 0.8)) * 50 - i * 15
            self.plaques_positions.append((x, y))
    
    def maj_volume(self):
        """Met à jour le volume des sons"""
        volumes = self.gestionnaire_config.volumes
        volume = volumes.get("effets", 50) / 100
        self.son_select.set_volume(volume)
        self.son_piece.set_volume(volume)
        for son in self.sons_portail:
            son.set_volume(volume)
        for son in self.sons_teleport:
            son.set_volume(volume)
    
    def dessiner_etoiles(self, ecran):
        """Dessine les étoiles scintillantes"""
        for etoile in self.etoiles:
            x, y, taille, brillance_base, vitesse, phase = etoile
            # Scintillement
            brillance = int(brillance_base * (0.5 + 0.5 * math.sin(self.temps_global * vitesse + phase)))
            brillance = max(50, min(255, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (x, y), taille)
    
    def dessiner_planete(self, ecran, planete, echelle=1.0, pos_x=None, pos_y=None):
        """Dessine une planète avec des effets visuels"""
        if pos_x:
            x = pos_x
        else:
            x = planete["x"]
        if pos_y:
            y = pos_y
        else:
            y = planete["y"]
        rayon = int(planete["rayon"] * echelle)
        couleur = planete["couleur"]
        
        # Ombre de la planète
        ombre_surface = pygame.Surface((rayon * 2 + 20, rayon * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(ombre_surface, (0, 0, 0, 80), (rayon + 10, rayon + 10), rayon + 5)
        ecran.blit(ombre_surface, (x - rayon - 10, y - rayon - 5))
        
        # Corps de la planète (dégradé simulé avec plusieurs cercles)
        for i in range(5):
            r = max(0, min(255, couleur[0] + i * 15 - 30))
            g = max(0, min(255, couleur[1] + i * 15 - 30))
            b = max(0, min(255, couleur[2] + i * 15 - 30))
            rayon_courant = rayon - i * (rayon // 8)
            offset_x = -i * 2
            offset_y = -i * 2
            pygame.draw.circle(ecran, (r, g, b), (x + offset_x, y + offset_y), max(1, rayon_courant))
        
        # Reflet lumineux
        reflet_surface = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
        pygame.draw.circle(reflet_surface, (255, 255, 255, 40), (rayon // 2, rayon // 2), rayon // 3)
        ecran.blit(reflet_surface, (x - rayon, y - rayon))
        
        # Anneaux si la planète en a
        if planete["anneaux"]:
            anneau_surface = pygame.Surface((rayon * 4, rayon * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(anneau_surface, (*couleur[:3], 100), (0, rayon // 2, rayon * 4, rayon))
            pygame.draw.ellipse(anneau_surface, (0, 0, 0, 0), (rayon // 2, rayon // 2 + rayon // 4, rayon * 3, rayon // 2))
            ecran.blit(anneau_surface, (x - rayon * 2, y - rayon))
        
        # Cratères/détails
        random.seed(hash(planete["nom"]))  # Même cratères pour chaque planète
        for i in range(3):
            cx = x + random.randint(-rayon // 2, rayon // 2)
            cy = y + random.randint(-rayon // 2, rayon // 2)
            cr = random.randint(rayon // 10, rayon // 5)
            couleur_cratere = (max(0, couleur[0] - 40), max(0, couleur[1] - 40), max(0, couleur[2] - 40))
            pygame.draw.circle(ecran, couleur_cratere, (cx, cy), cr)
        random.seed()  # Reset seed
        
        return pygame.Rect(x - rayon, y - rayon, rayon * 2, rayon * 2)
    
    def dessiner_portail(self, ecran, x, y, taille):
        """Dessine un portail de téléportation jaune/doré"""
        # Effet de rotation et pulsation
        pulse = 1 + 0.2 * math.sin(self.portail_animation * 0.3)
        rayon = int(taille * pulse)
        
        # Cercles concentriques pour l'effet de portail
        for i in range(5):
            alpha = 180 - i * 35
            r = rayon - i * (rayon // 6)
            if r > 0:
                # Couleur jaune/dorée avec variation
                teinte = 200 + int(55 * math.sin(self.portail_animation * 0.2 + i))
                surface = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, teinte, 50, alpha), (r + 5, r + 5), r)
                ecran.blit(surface, (x - r - 5, y - r - 5))
        
        # Particules tourbillonnantes
        for i in range(8):
            angle = self.portail_animation * 0.15 + i * (math.pi / 4)
            dist = rayon * 0.7
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            particle_size = 3 + int(2 * math.sin(self.portail_animation * 0.4 + i))
            pygame.draw.circle(ecran, (255, 255, 150), (px, py), particle_size)
        
        # Centre brillant
        pygame.draw.circle(ecran, (255, 255, 200), (x, y), rayon // 4)
    
    def dessiner_plaque_niveau(self, ecran, x, y, numero, est_debloque, est_survole, planete):
        """Dessine une plaque de niveau au sol"""
        largeur = 70
        hauteur = 40
        
        # Couleur selon l'état
        if est_debloque:
            # Utiliser la couleur de la planète pour les plaques débloquées
            couleur_base = planete["couleur"]
            if est_survole:
                couleur = (min(255, couleur_base[0] + 40), min(255, couleur_base[1] + 40), min(255, couleur_base[2] + 40))
                bordure = (min(255, couleur_base[0] + 80), min(255, couleur_base[1] + 80), min(255, couleur_base[2] + 80))
            else:
                couleur = couleur_base
                bordure = (min(255, couleur_base[0] + 30), min(255, couleur_base[1] + 30), min(255, couleur_base[2] + 30))
        else:
            if est_survole:
                couleur = (100, 100, 100)
                bordure = (150, 150, 150)
            else:
                couleur = (70, 70, 70)
                bordure = (100, 100, 100)
        
        # Effet de perspective (trapèze)
        points = [
            (x - largeur // 2 + 5, y - hauteur // 2),
            (x + largeur // 2 - 5, y - hauteur // 2),
            (x + largeur // 2, y + hauteur // 2),
            (x - largeur // 2, y + hauteur // 2)
        ]
        pygame.draw.polygon(ecran, couleur, points)
        pygame.draw.polygon(ecran, bordure, points, 3)
        
        # Lueur si débloqué et survolé
        if est_debloque and est_survole:
            lueur = pygame.Surface((largeur + 20, hauteur + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(lueur, (100, 255, 100, 50), (0, 0, largeur + 20, hauteur + 20))
            ecran.blit(lueur, (x - largeur // 2 - 10, y - hauteur // 2 - 10))
        
        # Numéro ou cadenas
        if est_debloque:
            texte = self.font_2.render(str(numero), True, (255, 255, 255))
            ecran.blit(texte, (x - texte.get_width() // 2, y - texte.get_height() // 2))
        else:
            ecran.blit(self.image_cadenas, (x - 15, y - 15))
        
        return pygame.Rect(x - largeur // 2, y - hauteur // 2, largeur, hauteur)
    
    def dessiner_sol_planete(self, ecran, planete):
        """Dessine le sol de la planète en vue zoomée"""
        couleur = planete["couleur"]
        
        # Sol courbé
        points_sol = [(0, HAUTEUR_ECRAN)]
        for x in range(0, LARGEUR_ECRAN + 50, 50):
            y = HAUTEUR_ECRAN - 100 + int(30 * math.sin(x * 0.005))
            points_sol.append((x, y))
        points_sol.append((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        
        # Couleur du sol (plus foncée que la planète)
        couleur_sol = (max(0, couleur[0] - 30), max(0, couleur[1] - 30), max(0, couleur[2] - 30))
        pygame.draw.polygon(ecran, couleur_sol, points_sol)
        
        # Ligne de surface
        couleur_surface = (min(255, couleur[0] + 20), min(255, couleur[1] + 20), min(255, couleur[2] + 20))
        pygame.draw.lines(ecran, couleur_surface, False, points_sol[1:-1], 3)
        
        # Quelques détails (rochers, herbe stylisée)
        random.seed(hash(planete["nom"]) + 42)
        for i in range(10):
            rx = random.randint(50, LARGEUR_ECRAN - 50)
            ry = HAUTEUR_ECRAN - 100 + int(30 * math.sin(rx * 0.005)) - random.randint(5, 20)
            rw = random.randint(20, 40)
            rh = random.randint(10, 25)
            couleur_detail = (max(0, couleur[0] - 50), max(0, couleur[1] - 50), max(0, couleur[2] - 50))
            pygame.draw.ellipse(ecran, couleur_detail, (rx, ry, rw, rh))
        random.seed()
    
    def afficher_galaxie(self, ecran):
        """Affiche la vue galaxie avec les planètes et effet de swipe entre univers"""
        # Fond étoilé
        ecran.fill((10, 10, 30))
        self.dessiner_etoiles(ecran)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Dessiner tous les univers visibles (actuel + voisins si en transition)
        for univers_idx, univers in enumerate(self.univers):
            # Position X de base de cet univers
            univers_base_x = univers_idx * LARGEUR_ECRAN
            # Décalage par rapport à la caméra
            offset_univers = univers_base_x - self.camera_x
            
            # Ne dessiner que si l'univers est visible à l'écran (optimisation)
            if offset_univers < -LARGEUR_ECRAN or offset_univers > LARGEUR_ECRAN:
                continue
            
            # Titre de l'univers
            titre = self.font_1.render(univers["nom"], True, (255, 255, 255))
            titre_x = LARGEUR_ECRAN // 2 - titre.get_width() // 2 + offset_univers
            ecran.blit(titre, (titre_x, 30))
            
            # Dessiner les planètes de cet univers
            planetes_univers = univers["planetes"]
            
            for i, planete in enumerate(planetes_univers):
                # Position X avec décalage de caméra
                planete_x = planete["x"] + offset_univers
                
                # Ne dessiner que si la planète est visible
                if planete_x < -100 or planete_x > LARGEUR_ECRAN + 100:
                    continue
                
                # Calculer le numéro de niveau global
                premier_niveau = univers_idx * self.nombre_planetes_par_univers * self.niveaux_par_planete + i * self.niveaux_par_planete + 1
                planete_debloquee = premier_niveau <= self.niveau_max_debloque
                
                # Animation de flottement
                offset_y = int(8 * math.sin(self.temps_global * 0.03 + i * 1.5 + univers_idx * 2))
                
                # Échelle si survolé (seulement si c'est l'univers actuel et pas en transition)
                rect = pygame.Rect(planete_x - planete["rayon"], planete["y"] - planete["rayon"] + offset_y,
                                 planete["rayon"] * 2, planete["rayon"] * 2)
                
                est_survole = (rect.collidepoint(mouse_pos) and planete_debloquee and 
                              univers_idx == self.univers_actuel and not self.transition_univers)
                if est_survole:
                    echelle = 1.1
                else:
                    echelle = 1.0
                
                # Dessiner la planète (grisée si verrouillée)
                if planete_debloquee:
                    self.dessiner_planete(ecran, planete, echelle, planete_x, planete["y"] + offset_y)
                else:
                    # Version grisée
                    planete_grise = planete.copy()
                    c = planete["couleur"]
                    gris = (c[0] + c[1] + c[2]) // 3
                    planete_grise["couleur"] = (gris // 2, gris // 2, gris // 2)
                    self.dessiner_planete(ecran, planete_grise, echelle, planete_x, planete["y"] + offset_y)
                    # Cadenas
                    ecran.blit(self.image_cadenas, (planete_x - 15, planete["y"] + offset_y - 15))
                
                # Nom de la planète
                if planete_debloquee:
                    couleur_nom = (255, 255, 255)
                else:
                    couleur_nom = (150, 150, 150)
                nom = self.font_petit.render(planete["nom"], True, couleur_nom)
                ecran.blit(nom, (planete_x - nom.get_width() // 2, planete["y"] + planete["rayon"] + 20 + offset_y))
                
                # Niveaux disponibles
                niveaux_texte = f"Niveaux {premier_niveau}-{premier_niveau + self.niveaux_par_planete - 1}"
                if planete_debloquee:
                    couleur_niveaux = (200, 200, 200)
                else:
                    couleur_niveaux = (100, 100, 100)
                niveaux_surface = self.font_petit.render(niveaux_texte, True, couleur_niveaux)
                ecran.blit(niveaux_surface, (planete_x - niveaux_surface.get_width() // 2, planete["y"] + planete["rayon"] + 45 + offset_y))
        
        # Dessiner les flèches de navigation entre univers
        self.dessiner_fleches_univers(ecran, mouse_pos)
        
        # Bouton retour
        self.dessiner_bouton_retour(ecran)
        
        # Version
        
        # Compteur de pièces
        self.dessiner_compteur_pieces(ecran)
        
        # Bouton Marché
        self.dessiner_bouton_marche(ecran)
    
    def univers_est_complete(self, index_univers):
        """Vérifie si tous les niveaux d'un univers sont terminés"""
        # Calculer le dernier niveau de l'univers
        dernier_niveau_univers = (index_univers + 1) * self.nombre_planetes_par_univers * self.niveaux_par_planete
        # L'univers est complété si le joueur a débloqué le niveau suivant (donc terminé tous les niveaux de cet univers)
        return self.niveau_max_debloque > dernier_niveau_univers
    
    def dessiner_fleches_univers(self, ecran, mouse_pos):
        """Dessine les flèches de navigation entre univers avec animation"""
        # Ne pas afficher les flèches pendant la transition
        if self.transition_univers:
            return
        
        # Animation de flottement
        offset_y = int(6 * math.sin(self.temps_global * 0.04))
        
        # Flèche droite (si univers suivant existe)
        if self.univers_actuel < len(self.univers) - 1:
            univers_debloque = self.univers_est_complete(self.univers_actuel)
            est_survole = self.fleche_droite_rect.collidepoint(mouse_pos)
            nom_univers_suivant = self.univers[self.univers_actuel + 1]["nom"]
            self.dessiner_fleche(ecran, self.fleche_droite_rect.centerx, self.fleche_droite_rect.centery + offset_y, 
                               "droite", est_survole, nom_univers_suivant, univers_debloque)
        
        # Flèche gauche (si univers précédent existe)
        if self.univers_actuel > 0:
            est_survole = self.fleche_gauche_rect.collidepoint(mouse_pos)
            nom_univers_precedent = self.univers[self.univers_actuel - 1]["nom"]
            self.dessiner_fleche(ecran, self.fleche_gauche_rect.centerx, self.fleche_gauche_rect.centery + offset_y, 
                               "gauche", est_survole, nom_univers_precedent, True)
    
    def dessiner_fleche(self, ecran, x, y, direction, est_survole, nom_univers="", est_debloque=True):
        """Dessine une flèche stylisée avec effets"""
        if est_survole and est_debloque:
            taille = 50
        else:
            taille = 42
        
        # Couleur selon l'état
        if not est_debloque:
            # Gris si verrouillé
            couleur = (80, 80, 90)
            bordure_couleur = (50, 50, 60)
        elif est_survole:
            # Effet de pulsation pour la couleur
            pulse = 0.7 + 0.3 * math.sin(self.temps_global * 0.1)
            couleur = (255, 255, int(150 + 105 * pulse))  # Jaune-blanc pulsant
            bordure_couleur = (255, 220, 100)
        else:
            couleur = (200, 200, 220)
            bordure_couleur = (150, 150, 180)
        
        # Effet de lueur étoilée si survolé et débloqué (petites étoiles autour)
        if est_survole and est_debloque:
            for i in range(5):
                angle = self.temps_global * 0.05 + i * (2 * math.pi / 5)
                rayon_etoile = 55 + 12 * math.sin(self.temps_global * 0.08 + i)
                ex = x + int(rayon_etoile * math.cos(angle))
                ey = y + int(rayon_etoile * math.sin(angle))
                taille_etoile = 3 + int(2 * math.sin(self.temps_global * 0.1 + i))
                brillance = int(150 + 105 * math.sin(self.temps_global * 0.15 + i))
                pygame.draw.circle(ecran, (brillance, brillance, int(brillance * 0.7)), (ex, ey), taille_etoile)
        
        # Points du triangle
        if direction == "droite":
            points = [
                (x - taille // 2, y - taille // 2),
                (x + taille // 2, y),
                (x - taille // 2, y + taille // 2)
            ]
        else:  # gauche
            points = [
                (x + taille // 2, y - taille // 2),
                (x - taille // 2, y),
                (x + taille // 2, y + taille // 2)
            ]
        
        # Dessiner le triangle avec bordure
        pygame.draw.polygon(ecran, couleur, points)
        pygame.draw.polygon(ecran, bordure_couleur, points, 3)
        
        # Dessiner le cadenas si verrouillé (centré sur le triangle)
        if not est_debloque:
            cadenas_largeur = self.image_cadenas.get_width()
            cadenas_hauteur = self.image_cadenas.get_height()
            cadenas_x = x - cadenas_largeur // 2
            cadenas_y = y - cadenas_hauteur // 2
            ecran.blit(self.image_cadenas, (cadenas_x, cadenas_y))
        
        # Afficher le nom de l'univers destination à côté si survolé (même si verrouillé)
        if est_survole and nom_univers:
            texte = self.font_petit.render(nom_univers, True, (255, 255, 200))
            # Positionner le texte vers l'intérieur de l'écran
            if direction == "droite":
                texte_x = x - taille - texte.get_width() - 15
            else:
                texte_x = x + taille + 15
            texte_y = y - texte.get_height() // 2
            # Fond semi-transparent pour le texte
            fond = pygame.Surface((texte.get_width() + 10, texte.get_height() + 6), pygame.SRCALPHA)
            fond.fill((0, 0, 30, 180))
            ecran.blit(fond, (texte_x - 5, texte_y - 3))
            ecran.blit(texte, (texte_x, texte_y))
    
    def afficher_planete(self, ecran):
        """Affiche la vue planète avec les niveaux"""
        planete = self.planetes[self.planete_selectionnee]
        
        # Fond avec dégradé (ciel de la planète)
        couleur = planete["couleur"]
        for y in range(HAUTEUR_ECRAN):
            ratio = y / HAUTEUR_ECRAN
            r = int(10 + ratio * couleur[0] * 0.3)
            g = int(10 + ratio * couleur[1] * 0.3)
            b = int(30 + ratio * couleur[2] * 0.3)
            pygame.draw.line(ecran, (r, g, b), (0, y), (LARGEUR_ECRAN, y))
        
        # Étoiles
        for etoile in self.etoiles:
            x, y, taille, brillance_base, vitesse, phase = etoile
            if y < HAUTEUR_ECRAN * 0.6:
                # Scintillement animé même dans la vue planète
                brillance = int(brillance_base * (0.5 + 0.5 * math.sin(self.temps_global * vitesse + phase)))
                brillance = max(50, min(255, brillance))
                pygame.draw.circle(ecran, (brillance, brillance, brillance), (x, y), taille)
        
        # Sol de la planète
        self.dessiner_sol_planete(ecran, planete)
        
        # Titre
        titre = self.font_1.render(planete["nom"], True, (255, 255, 255))
        ecran.blit(titre, (LARGEUR_ECRAN // 2 - titre.get_width() // 2, 30))
        
        # Dessiner les plaques de niveaux
        mouse_pos = pygame.mouse.get_pos()
        premier_niveau = self.univers_actuel * self.nombre_planetes_par_univers * self.niveaux_par_planete + self.planete_selectionnee * self.niveaux_par_planete + 1
        
        for i, (px, py) in enumerate(self.plaques_positions):
            numero = premier_niveau + i
            est_debloque = numero <= self.niveau_max_debloque
            rect = pygame.Rect(px - 35, py - 20, 70, 40)
            est_survole = rect.collidepoint(mouse_pos)
            self.dessiner_plaque_niveau(ecran, px, py, numero, est_debloque, est_survole, planete)
        
        # Dessiner le portail si actif
        if self.portail_actif:
            self.dessiner_portail(ecran, self.portail_x, self.portail_y - 30, 40)
        
        # Dessiner le mage
        if self.mage_visible:
            # Choisir le bon sprite
            if self.mage_en_saut:
                # Animation de saut
                t = self.mage_saut_progression
                if t < 0.15:
                    # Début du saut
                    sprite = self.mage_walk_frames[1]
                elif t < 0.2:
                    # Milieu du saut
                    sprite = self.mage_walk_frames[2]
                else:
                    # Fin du saut
                    sprite = self.mage_walk_frames[3]
                
                if self.mage_direction < 0:
                    sprite = pygame.transform.flip(sprite, True, False)
            elif self.mage_en_mouvement:
                sprite = self.mage_walk_frames[self.mage_frame_index % len(self.mage_walk_frames)]
                if self.mage_direction < 0:
                    sprite = pygame.transform.flip(sprite, True, False)
            else:
                if self.mage_direction >= 0:
                    sprite = self.mage_sprite
                else:
                    sprite = self.mage_sprite_flip
            
            ecran.blit(sprite, (self.mage_x - 30, self.mage_y - 55))
        
        # Bouton retour
        self.dessiner_bouton_retour(ecran, "Retour")
        
        # Compteur de pièces
        self.dessiner_compteur_pieces(ecran)
    
    def dessiner_compteur_pieces(self, ecran):
        """Dessine le compteur de pièces en haut à droite"""
        total = self.pieces_total_cache
        texte = self.font_2.render(str(total), True, (255, 215, 0))
        marge_droite = 40
        y_align = 30
        x_texte = LARGEUR_ECRAN - marge_droite - texte.get_width()
        x_icone = x_texte - 56
        y_icone = y_align
        y_texte = y_align + (48 - texte.get_height()) // 2
        ecran.blit(self.icone_piece, (x_icone, y_icone))
        ecran.blit(texte, (x_texte, y_texte))
    
    def dessiner_bouton_marche(self, ecran):
        """Dessine le bouton Marché en haut à gauche"""
        mouse_pos = pygame.mouse.get_pos()
        est_survole = self.bouton_marche.collidepoint(mouse_pos)
        if est_survole:
            couleur = COULEUR_SURVOL
        else:
            couleur = COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur, self.bouton_marche, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_marche, 3, border_radius=10)
        texte_surface = self.font_3.render("Marché", True, (255, 255, 255))
        # Texte + icône
        icone_w = self.icone_marche.get_width()
        icone_h = self.icone_marche.get_height()
        espacement = 8
        largeur_totale = texte_surface.get_width() + espacement + icone_w
        x_debut = self.bouton_marche.centerx - largeur_totale // 2
        y_icone = self.bouton_marche.centery - icone_h // 2
        y_texte = self.bouton_marche.centery - texte_surface.get_height() // 2
        ecran.blit(texte_surface, (x_debut, y_texte))
        ecran.blit(self.icone_marche, (x_debut + texte_surface.get_width() + espacement, y_icone))
    
    def afficher_accueil_marche(self, ecran):
        """Affiche l'accueil du marché : les catégories sous forme de boutons."""
        mouse_pos = pygame.mouse.get_pos()
        self.boutons_categories = []

        bouton_l, bouton_h = 250, 50
        ecart = 30
        nb = len(self.marche_categories)
        hauteur_totale = nb * bouton_h + (nb - 1) * ecart
        y_start = HAUTEUR_ECRAN // 2 - hauteur_totale // 2

        for i, cat in enumerate(self.marche_categories):
            x = LARGEUR_ECRAN // 2 - bouton_l // 2
            y = y_start + i * (bouton_h + ecart)
            rect = pygame.Rect(x, y, bouton_l, bouton_h)
            self.boutons_categories.append((rect, cat))

            dispo = cat.get("disponible", True)
            if dispo and rect.collidepoint(mouse_pos):
                couleur_fond = COULEUR_SURVOL
            else:
                couleur_fond = COULEUR_BOUTON
            pygame.draw.rect(ecran, couleur_fond, rect, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, rect, 3, border_radius=10)

            if dispo:
                couleur_txt = (255, 255, 255)
            else:
                couleur_txt = (150, 150, 150)
            nom_txt = self.font_2.render(cat["nom"], True, couleur_txt)
            ecran.blit(nom_txt, (rect.centerx - nom_txt.get_width() // 2,
                                 rect.centery - nom_txt.get_height() // 2))

            if not dispo:
                bientot = self.font_petit.render("Bientôt disponible", True, (180, 180, 180))
                ecran.blit(bientot, (rect.centerx - bientot.get_width() // 2, rect.bottom + 6))

    def afficher_marche(self, ecran):
        """Affiche la page du marché"""
        # Lancer la musique
        if not self.musique_marche_active:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(resource_path(os.path.join("assets/audio", "market.ogg")))
                vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(-1)
            except Exception:
                pass
            self.musique_marche_active = True
            # Recharger la config à l'ouverture du marché
            self.config = self.gestionnaire_config.charger_config()
            self.gestionnaire_config.config = self.config
            self.pieces_total_cache = self.config.get("pieces_total", 0)
            self.achat_en_attente = None
            self.marche_section = None

        ecran.fill((25, 18, 10))
        self.dessiner_etoiles(ecran)

        titre = self.font_1.render("Marché", True, (255, 215, 0))
        ecran.blit(titre, (LARGEUR_ECRAN // 2 - titre.get_width() // 2, 30))

        # Accueil du marché : choix de la catégorie
        if self.marche_section is None:
            self.afficher_accueil_marche(ecran)
            self.dessiner_compteur_pieces(ecran)
            self.dessiner_bouton_retour(ecran, "Retour")
            return

        # Sinon : afficher la section choisie
        if self.marche_section == "powerups":
            self.afficher_section_powerups(ecran)
        else:
            self.afficher_section_avatars(ecran)

        self.dessiner_compteur_pieces(ecran)
        self.dessiner_bouton_retour(ecran, "Retour")

        # Popup de confirmation d'achat
        if self.achat_en_attente is not None:
            self.dessiner_popup_achat(ecran, pygame.mouse.get_pos())

    def afficher_section_avatars(self, ecran):
        """Affiche la grille d'avatars du marché."""
        if self.avatars_marche_cache is None:
            self.construire_cache_avatars_marche()

        sous_titre = self.font_2.render("Avatars", True, (230, 200, 150))
        ecran.blit(sous_titre, (LARGEUR_ECRAN // 2 - sous_titre.get_width() // 2, 120))

        cellule = 120
        gap = 40
        colonnes = 7
        y_start = 200
        espace_y = 160
        nb = len(self.profil.avatars)

        mouse_pos = pygame.mouse.get_pos()
        self.boutons_achats = []

        for i, avatar in enumerate(self.profil.avatars):
            row = i // colonnes
            col = i % colonnes
            nb_rangee = min(colonnes, nb - row * colonnes)
            largeur_rangee = nb_rangee * cellule + (nb_rangee - 1) * gap
            x_start = (LARGEUR_ECRAN - largeur_rangee) // 2
            x = x_start + col * (cellule + gap)
            y = y_start + row * espace_y

            rect_avatar = pygame.Rect(x, y, cellule, cellule)
            dispo = self.profil.avatar_est_disponible_marche(i)
            possede = self.profil.avatar_est_debloque(i)
            prix = avatar.get("prix", 0)

            self.boutons_achats.append((rect_avatar, i, possede, dispo, prix))

            if not dispo:
                couleur_case = (0, 0, 0)
            elif rect_avatar.collidepoint(mouse_pos) and self.achat_en_attente is None:
                couleur_case = COULEUR_SURVOL
            else:
                couleur_case = COULEUR_BOUTON

            pygame.draw.rect(ecran, couleur_case, rect_avatar, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, rect_avatar, 3, border_radius=10)

            if not dispo:
                # Afficher le cadenas et le niveau requis
                cad_x = rect_avatar.centerx - self.image_cadenas.get_width() // 2
                cad_y = rect_avatar.centery - self.image_cadenas.get_height() // 2
                ecran.blit(self.image_cadenas, (cad_x, cad_y))
                niv_req = avatar.get("niveau_associe", "?")
                txt_niv = self.font_petit.render(f"Niv.{niv_req}", True, (255, 100, 100))
                ecran.blit(txt_niv, (x + cellule // 2 - txt_niv.get_width() // 2, y + cellule - 28))
                continue

            # Avatar disponible : afficher l'image
            img = self.avatars_marche_cache[i]
            if img is not None:
                ecran.blit(img, (x + (cellule - img.get_width()) // 2, y + 10))

            if possede:
                txt = self.font_petit.render("Acquis", True, (100, 255, 100))
                ecran.blit(txt, (x + cellule // 2 - txt.get_width() // 2, y + cellule - 28))
            else:
                txt_prix = self.font_petit.render(f"{prix}", True, (255, 215, 0))
                piece_img = pygame.transform.scale(self.icone_piece, (20, 20))
                ecart = 5
                total_w = piece_img.get_width() + ecart + txt_prix.get_width()
                gx = x + cellule // 2 - total_w // 2
                center_y = y + cellule - 16
                ecran.blit(piece_img, (gx, center_y - piece_img.get_height() // 2))
                ecran.blit(txt_prix, (gx + piece_img.get_width() + ecart, center_y - txt_prix.get_height() // 2))

    def afficher_section_powerups(self, ecran):
        """Affiche les power-ups du marché sous forme de cartes.
        """
        if self.powerups_marche_cache is None:
            self.construire_cache_powerups_marche()

        sous_titre = self.font_2.render("Power-ups", True, (230, 200, 150))
        ecran.blit(sous_titre, (LARGEUR_ECRAN // 2 - sous_titre.get_width() // 2, 120))

        mouse_pos = pygame.mouse.get_pos()
        self.boutons_powerups = []

        carte_l, carte_h = 720, 180
        ecart_v = 30
        y_start = 210

        for i, powerup in enumerate(self.profil.powerups):
            x = (LARGEUR_ECRAN - carte_l) // 2
            y = y_start + i * (carte_h + ecart_v)
            rect = pygame.Rect(x, y, carte_l, carte_h)

            possede = self.profil.powerup_est_achete(i)
            dispo = self.profil.powerup_est_disponible_marche(i)
            prix = powerup.get("prix", 0)
            self.boutons_powerups.append((rect, i, possede, dispo, prix))

            if not dispo:
                couleur_case = (0, 0, 0)
            elif rect.collidepoint(mouse_pos) and not possede and self.achat_en_attente is None:
                couleur_case = COULEUR_SURVOL
            else:
                couleur_case = COULEUR_BOUTON
            pygame.draw.rect(ecran, couleur_case, rect, border_radius=12)
            pygame.draw.rect(ecran, COULEUR_BORDURE, rect, 3, border_radius=12)

            img = self.powerups_marche_cache[i]
            img_x = rect.left + 30
            texte_x = img_x + (img.get_width() if img is not None else 120) + 40

            # Power-up verrouillé
            if not dispo:
                cad_x = img_x + (img.get_width() if img is not None else 120) // 2 - self.image_cadenas.get_width() // 2
                cad_y = rect.centery - self.image_cadenas.get_height() // 2
                ecran.blit(self.image_cadenas, (cad_x, cad_y))
                titre_pw = self.font_2.render(powerup["nom"], True, (150, 150, 150))
                ecran.blit(titre_pw, (texte_x, rect.top + 50))
                niv_req = powerup.get("niveau_associe", "?")
                txt_niv = self.font_3.render(f"Niveau {niv_req} requis", True, (255, 100, 100))
                ecran.blit(txt_niv, (texte_x, rect.top + 95))
                continue

            # Image
            if img is not None:
                img_y = rect.top + 20
                ecran.blit(img, (img_x, img_y))
                img_centre_x = img_x + img.get_width() // 2
                bas_image = img_y + img.get_height()
            else:
                img_centre_x = img_x + 60
                bas_image = rect.top + 140

            # Prix (ou "Acquis")
            if possede:
                txt = self.font_petit.render("Acquis", True, (100, 255, 100))
                ecran.blit(txt, (img_centre_x - txt.get_width() // 2, bas_image + 8))
            else:
                txt_prix = self.font_3.render(f"{prix}", True, (255, 215, 0))
                piece_img = pygame.transform.scale(self.icone_piece, (26, 26))
                ecart = 6
                total_w = piece_img.get_width() + ecart + txt_prix.get_width()
                gx = img_centre_x - total_w // 2
                cy = bas_image + 8 + txt_prix.get_height() // 2
                ecran.blit(piece_img, (gx, cy - piece_img.get_height() // 2))
                ecran.blit(txt_prix, (gx + piece_img.get_width() + ecart, cy - txt_prix.get_height() // 2))

            # Titre et description
            titre_pw = self.font_2.render(powerup["nom"], True, (255, 255, 255))
            ecran.blit(titre_pw, (texte_x, rect.top + 30))

            desc_y = rect.top + 80
            for ligne in powerup.get("description", []):
                ligne_txt = self.font_petit.render(ligne, True, (200, 200, 200))
                ecran.blit(ligne_txt, (texte_x, desc_y))
                desc_y += 30

    def dessiner_popup_achat(self, ecran, mouse_pos):
        """Dessine la fenêtre de confirmation d'achat"""
        type_achat, idx = self.achat_en_attente
        if type_achat == "powerup":
            article = self.profil.powerups[idx]
        else:
            article = self.profil.avatars[idx]
        prix = article.get("prix", 0)

        # Fond
        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        ecran.blit(overlay, (0, 0))

        # Boîte
        largeur, hauteur = 540, 280
        boite = pygame.Rect((LARGEUR_ECRAN - largeur) // 2, (HAUTEUR_ECRAN - hauteur) // 2, largeur, hauteur)
        pygame.draw.rect(ecran, (45, 35, 25), boite, border_radius=15)
        pygame.draw.rect(ecran, (255, 215, 0), boite, 3, border_radius=15)

        # Titre
        titre = self.font_3.render("Confirmer l'achat", True, (255, 215, 0))
        ecran.blit(titre, (boite.centerx - titre.get_width() // 2, boite.top + 25))

        # nom de l'article
        nom = self.font_3.render(article["nom"], True, (255, 255, 255))
        ecran.blit(nom, (boite.centerx - nom.get_width() // 2, boite.top + 80))

        # prix
        prix_txt = self.font_2.render(f"{prix}", True, (255, 215, 0))
        piece_img = pygame.transform.scale(self.icone_piece, (36, 36))
        ecart = 8
        total_w = piece_img.get_width() + ecart + prix_txt.get_width()
        gx = boite.centerx - total_w // 2
        center_y = boite.top + 125 + 18
        ecran.blit(piece_img, (gx, center_y - piece_img.get_height() // 2))
        ecran.blit(prix_txt, (gx + piece_img.get_width() + ecart, center_y - prix_txt.get_height() // 2))

        # Boutons Confirmer Annuler
        if self.bouton_achat_confirmer.collidepoint(mouse_pos):
            pygame.draw.rect(ecran, (60, 180, 60), self.bouton_achat_confirmer, border_radius=10)
        else:
            pygame.draw.rect(ecran, (40, 150, 40), self.bouton_achat_confirmer, border_radius=10)
        pygame.draw.rect(ecran, (255, 255, 255), self.bouton_achat_confirmer, 2, border_radius=10)
        conf_txt = self.font_3.render("Acheter", True, (255, 255, 255))
        ecran.blit(conf_txt, (self.bouton_achat_confirmer.centerx - conf_txt.get_width() // 2,
                              self.bouton_achat_confirmer.centery - conf_txt.get_height() // 2))

        if self.bouton_achat_annuler.collidepoint(mouse_pos):
            pygame.draw.rect(ecran, (180, 60, 60), self.bouton_achat_annuler, border_radius=10)
        else:
            pygame.draw.rect(ecran, (150, 40, 40), self.bouton_achat_annuler, border_radius=10)
        pygame.draw.rect(ecran, (255, 255, 255), self.bouton_achat_annuler, 2, border_radius=10)
        ann_txt = self.font_3.render("Annuler", True, (255, 255, 255))
        ecran.blit(ann_txt, (self.bouton_achat_annuler.centerx - ann_txt.get_width() // 2,
                             self.bouton_achat_annuler.centery - ann_txt.get_height() // 2))

    def gerer_clic_marche(self, pos):
        """Gère les clics dans le marché : choix de catégorie, puis achats"""
        # Accueil
        if self.marche_section is None:
            for rect, cat in self.boutons_categories:
                if rect.collidepoint(pos) and cat.get("disponible", True):
                    self.son_select.play()
                    self.marche_section = cat["section"]
                    return None
            return None

        if self.achat_en_attente is not None:
            if self.bouton_achat_confirmer.collidepoint(pos):
                self.confirmer_achat(self.achat_en_attente)
                self.achat_en_attente = None
            elif self.bouton_achat_annuler.collidepoint(pos):
                self.son_select.play()
                self.achat_en_attente = None
            return None

        # Section power-ups
        if self.marche_section == "powerups":
            for rect, idx, possede, dispo, prix in self.boutons_powerups:
                if rect.collidepoint(pos):
                    if dispo and not possede and self.config.get("pieces_total", 0) >= prix:
                        self.son_select.play()
                        self.achat_en_attente = ("powerup", idx)
                    return None
            return None

        # Section avatars
        for rect, idx, possede, dispo, prix in self.boutons_achats:
            if rect.collidepoint(pos):
                if dispo and not possede and self.config.get("pieces_total", 0) >= prix:
                    self.son_select.play()
                    self.achat_en_attente = ("avatar", idx)
                return None
        return None

    def confirmer_achat(self, achat):
        """Valide un achat : débite les pièces et enregistre la possession"""
        type_achat, idx = achat
        if type_achat == "powerup":
            article = self.profil.powerups[idx]
        else:
            article = self.profil.avatars[idx]
        prix = article.get("prix", 0)
        # Recharger le fichier pour avoir le solde de pièces à jour
        config = self.gestionnaire_config.charger_config()
        if config.get("pieces_total", 0) < prix:
            return
        self.son_piece.play()
        config["pieces_total"] = config.get("pieces_total", 0) - prix
        if type_achat == "powerup":
            achetes = config.get("powerups_achetes", [])
            if article["id"] not in achetes:
                achetes.append(article["id"])
            config["powerups_achetes"] = achetes
        else:
            achetes = config.get("avatars_achetes", [0])
            if idx not in achetes:
                achetes.append(idx)
            config["avatars_achetes"] = achetes
        self.gestionnaire_config.sauvegarder_config(config)
        self.config = config
        self.pieces_total_cache = config["pieces_total"]
    
    def quitter_marche(self):
        """Quitte le marché et restaure la musique précédente"""
        self.musique_marche_active = False
        self.achat_en_attente = None
        # Restaurer la musique selon l'état
        try:
            pygame.mixer.music.stop()
            if self.etat_menu == "planete":
                planete = self.planetes[self.planete_selectionnee]
                nom_planete = planete["nom"].lower()
                chemin_musique = resource_path(os.path.join("assets/audio", nom_planete + ".ogg"))
                if os.path.exists(chemin_musique):
                    pygame.mixer.music.load(chemin_musique)
                else:
                    pygame.mixer.music.load(resource_path(os.path.join("assets/audio", "main_theme.ogg")))
            else:
                pygame.mixer.music.load(resource_path(os.path.join("assets/audio", "main_theme.ogg")))
            vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
        except Exception:
            pass
    
    def dessiner_bouton_retour(self, ecran, texte="Retour"):
        """Dessine le bouton retour"""
        mouse_pos = pygame.mouse.get_pos()
        est_survole = self.bouton_retour.collidepoint(mouse_pos)
        
        if est_survole:
            couleur = COULEUR_SURVOL
        else:
            couleur = COULEUR_BOUTON
        pygame.draw.rect(ecran, couleur, self.bouton_retour, border_radius=10)
        pygame.draw.rect(ecran, COULEUR_BORDURE, self.bouton_retour, 3, border_radius=10)
        
        texte_surface = self.font_2.render(texte, True, (255, 255, 255))
        ecran.blit(texte_surface, (self.bouton_retour.centerx - texte_surface.get_width() // 2,
                                    self.bouton_retour.centery - texte_surface.get_height() // 2))
    
    def obtenir_info_planete(self, numero_niveau):
        """Retourne les informations de la planète pour un numéro de niveau donné"""
        # Calculer l'univers et la planète du niveau
        niveaux_par_univers = self.nombre_planetes_par_univers * self.niveaux_par_planete
        univers_idx = (numero_niveau - 1) // niveaux_par_univers
        niveau_dans_univers = (numero_niveau - 1) % niveaux_par_univers
        planete_idx = niveau_dans_univers // self.niveaux_par_planete
        
        # renvoyer les infos de la planète
        if univers_idx < len(self.univers):
            univers = self.univers[univers_idx]
            if planete_idx < len(univers["planetes"]):
                planete = univers["planetes"][planete_idx]
                return {
                    "nom": planete["nom"],
                    "couleur": planete["couleur"],
                    "univers": univers["nom"]
                }
  
    def afficher_transition_zoom(self, ecran):
        """Affiche la transition de zoom vers une planète"""
        planete = self.planetes[self.planete_selectionnee]
        
        # Interpoler entre les deux vues
        t = self.zoom_animation
        
        # Fond qui s'éclaircit progressivement
        ecran.fill((int(10 + t * 20), int(10 + t * 20), int(30 + t * 20)))
        
        if t < 0.5:
            # Première moitié : zoom sur la planète
            self.dessiner_etoiles(ecran)
            echelle = 1 + t * 10
            self.dessiner_planete(ecran, planete, echelle, LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2)
        else:
            # Deuxième moitié : fondu vers la vue planète
            alpha = int((t - 0.5) * 2 * 255)
            self.afficher_planete(ecran)
    
    def afficher_selection(self, ecran):
        """Affiche le menu de sélection des niveaux"""
        if self.zoom_en_cours:
            self.afficher_transition_zoom(ecran)
        elif self.etat_menu == "marche":
            self.afficher_marche(ecran)
        elif self.etat_menu == "galaxie":
            self.afficher_galaxie(ecran)
        else:
            self.afficher_planete(ecran)

    def maj(self):
        """Met à jour les animations du menu"""
        self.temps_global += 1
        self.maj_animations()

    def recharger_donnees(self):
        """Recharge les données depuis le disque"""
        self.config = self.gestionnaire_config.charger_config()
        self.niveau_max_debloque = self.config.get("niveau_actuel", self.niveau_max_debloque)
        self.pieces_total_cache = self.config.get("pieces_total", 0)
        self.maj_volume()

    def maj_animations(self):
        """Met à jour toutes les animations"""
        # Animation de zoom
        if self.zoom_en_cours:
            self.zoom_animation += self.zoom_direction * self.vitesse_zoom
            if self.zoom_animation >= 1:
                self.zoom_animation = 1
                self.zoom_en_cours = False
                self.etat_menu = "planete"
                self.initialiser_position_mage()
            elif self.zoom_animation <= 0:
                self.zoom_animation = 0
                self.zoom_en_cours = False
                self.etat_menu = "galaxie"
        
        # Animation du mage qui saute
        if self.mage_en_mouvement and self.mage_en_saut:
            self.mage_saut_progression += 0.04  # Vitesse du saut
            
            if self.mage_saut_progression >= 1.0:
                # Saut terminé
                self.mage_saut_progression = 1.0
                self.mage_x = self.mage_cible_x
                self.mage_y = self.mage_cible_y
                self.mage_en_saut = False
                
                # Vérifier s'il y a encore des plaques dans le chemin
                if self.chemin_plaques and self.plaque_courante_index < len(self.chemin_plaques) - 1:
                    # Passer à la plaque suivante
                    self.plaque_courante_index += 1
                    next_plaque = self.chemin_plaques[self.plaque_courante_index]
                    self.mage_cible_x, self.mage_cible_y = self.plaques_positions[next_plaque]
                    # Mettre à jour la direction
                    new_dx = self.mage_cible_x - self.mage_x
                    if new_dx > 0:
                        self.mage_direction = 1
                    else:
                        self.mage_direction = -1
                    
                    # Démarrer un nouveau saut
                    self.mage_en_saut = True
                    self.mage_saut_progression = 0
                    self.mage_saut_start_x = self.mage_x
                    self.mage_saut_start_y = self.mage_y
                else:
                    # Arrivé à destination finale
                    self.mage_en_mouvement = False
                    self.chemin_plaques = []
                    self.plaque_courante_index = 0
                    # Activer le portail de téléportation
                    self.portail_actif = True
                    self.portail_x = self.mage_x
                    self.portail_y = self.mage_y
                    self.portail_animation = 0
                    self.teleportation_en_cours = True
            else:
                t = self.mage_saut_progression
                self.mage_x = self.mage_saut_start_x + (self.mage_cible_x - self.mage_saut_start_x) * t
                
                # saut en arc de cercle
                # https://stackoverflow.com/questions/3522032/how-to-make-a-character-jump-in-a-2d-game
                self.mage_y = (self.mage_saut_start_y + (self.mage_cible_y - self.mage_saut_start_y) * t - self.mage_hauteur_saut * math.sin(math.pi * t))
        
        # Animation du portail
        if self.portail_actif:
            self.portail_animation += 1
            
            # Séquence de téléportation
            if self.teleportation_en_cours:
                if self.portail_animation == 30:
                    # Le mage disparaît dans le portail
                    self.mage_visible = False
                elif self.portail_animation >= 60:
                    # Fin de l'animation, lancer le niveau
                    self.portail_actif = False
                    self.teleportation_en_cours = False
                    self.niveau_a_lancer = self.niveau_cible
            else:
                # Portail d'arrivée (quand on revient d'un niveau)
                if self.portail_animation >= 40:
                    self.mage_visible = True
                if self.portail_animation >= 60:
                    self.portail_actif = False
        
        # Animation de transition entre univers (interpolation de la caméra)
        if self.transition_univers:
            # Interpolation douce (easing)
            diff = self.camera_cible_x - self.camera_x
            self.camera_x += diff * self.camera_vitesse
            
            # Vérifier si on est arrivé (assez proche de la cible)
            if abs(diff) < 1:
                self.camera_x = self.camera_cible_x
                self.transition_univers = False
                self.univers_actuel = int(self.camera_x / LARGEUR_ECRAN)
                self.planetes = self.univers[self.univers_actuel]["planetes"]
    
    def initialiser_position_mage(self):
        """Place le mage sur sa position initiale"""
        # Trouver le niveau actuel du joueur sur cette planète
        premier_niveau = self.univers_actuel * self.nombre_planetes_par_univers * self.niveaux_par_planete + self.planete_selectionnee * self.niveaux_par_planete + 1
        niveau_local = min(self.niveau_max_debloque - premier_niveau + 1, self.niveaux_par_planete) - 1
        niveau_local = max(0, niveau_local)
        
        self.mage_niveau_actuel = niveau_local
        self.mage_x, self.mage_y = self.plaques_positions[niveau_local]
        self.mage_visible = True
        
        # Animation d'arrivée avec portail
        self.portail_actif = True
        self.portail_x = self.mage_x
        self.portail_y = self.mage_y
        self.portail_animation = 0
        self.mage_visible = False
        self.teleportation_en_cours = False  # C'est une arrivée, pas un départ
    
    def gerer_clic(self, pos):
        """Gère les clics selon l'état du menu"""
        # Ignorer les clics pendant les animations
        if self.zoom_en_cours or self.mage_en_mouvement or self.transition_univers:
            return None

        # Si portail actif et c'est un départ (teleportation_en_cours), bloquer tout pendant l'animation
        if self.portail_actif and self.teleportation_en_cours:
            return None
        # Si c'est un retour (pas de téléportation en cours) et le mage n'est pas encore visible, autoriser uniquement le bouton retour
        if self.portail_actif and not self.teleportation_en_cours and not self.mage_visible:
            if not self.bouton_retour.collidepoint(pos):
                return None
        
        # Bouton Marché
        if self.etat_menu == "galaxie" and self.bouton_marche.collidepoint(pos):
            self.son_select.play()
            return "marche"
        
        # Bouton retour
        if self.bouton_retour.collidepoint(pos):
            if self.etat_menu == "marche":
                # Si on est dans une section, revenir à l'accueil du marché
                if self.marche_section is not None:
                    self.son_select.play()
                    self.marche_section = None
                    self.achat_en_attente = None
                    return None
                # Sinon, quitter le marché
                self.son_select.play()
                self.quitter_marche()
                self.etat_menu = "galaxie"
                return None
            elif self.etat_menu == "planete":
                # Retour à la galaxie avec son de téléportation
                random.choice(self.sons_teleport).play()
                # Restaurer la musique principale
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(resource_path(os.path.join("assets/audio", "main_theme.ogg")))
                    vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
                    pygame.mixer.music.set_volume(vol)
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass
                self.zoom_en_cours = True
                self.zoom_direction = -1
                return None
            else:
                self.son_select.play()
                return 0  # Retour au menu principal
        
        if self.etat_menu == "marche":
            return self.gerer_clic_marche(pos)
        elif self.etat_menu == "galaxie":
            return self.gerer_clic_galaxie(pos)
        else:
            return self.gerer_clic_planete(pos)
    
    def gerer_clic_galaxie(self, pos):
        """Gère les clics sur la vue galaxie"""
        # Vérifier les flèches de navigation entre univers
        if self.univers_actuel < len(self.univers) - 1 and self.fleche_droite_rect.collidepoint(pos):
            # Vérifier si l'univers est débloqué
            if self.univers_est_complete(self.univers_actuel):
                self.son_select.play()
                self.changer_univers(1)
            return None
        
        if self.univers_actuel > 0 and self.fleche_gauche_rect.collidepoint(pos):
            self.son_select.play()
            self.changer_univers(-1)
            return None
        
        # Vérifier les clics sur les planètes de l'univers actuel
        planetes_univers = self.univers[self.univers_actuel]["planetes"]
        # Calculer l'offset de la caméra pour l'univers actuel
        offset_univers = self.univers_actuel * LARGEUR_ECRAN - self.camera_x
        
        for i, planete in enumerate(planetes_univers):
            # Calculer le numéro de niveau global
            premier_niveau = self.univers_actuel * self.nombre_planetes_par_univers * self.niveaux_par_planete + i * self.niveaux_par_planete + 1
            planete_debloquee = premier_niveau <= self.niveau_max_debloque
            
            if not planete_debloquee:
                continue
            
            # Vérifier si on clique sur la planète (avec offset de caméra)
            planete_x = planete["x"] + offset_univers
            offset_y = int(8 * math.sin(self.temps_global * 0.03 + i * 1.5))
            distance = math.sqrt((pos[0] - planete_x) ** 2 + (pos[1] - planete["y"] - offset_y) ** 2)
            
            if distance <= planete["rayon"]:
                random.choice(self.sons_teleport).play()
                self.planete_selectionnee = i
                self.planetes = planetes_univers  # Mettre à jour la référence
                
                # Charger la musique de la planète
                try:
                    nom_planete = planete["nom"].lower()
                    chemin_musique = resource_path(os.path.join("assets/audio", nom_planete + ".ogg"))
                    if os.path.exists(chemin_musique):
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(chemin_musique)
                        vol = self.gestionnaire_config.obtenir_volumes().get("musique", 50) / 100
                        pygame.mixer.music.set_volume(vol)
                        pygame.mixer.music.play(-1)
                except Exception:
                    pass
                
                # Initialiser immédiatement la position du mage pour éviter le flash
                premier_niveau_planete = self.univers_actuel * self.nombre_planetes_par_univers * self.niveaux_par_planete + self.planete_selectionnee * self.niveaux_par_planete + 1
                niveau_local = min(self.niveau_max_debloque - premier_niveau_planete + 1, self.niveaux_par_planete) - 1
                niveau_local = max(0, niveau_local)
                
                self.mage_niveau_actuel = niveau_local
                self.mage_x, self.mage_y = self.plaques_positions[niveau_local]
                self.mage_visible = False  # Caché jusqu'à l'animation de portail
                
                # Démarrer l'animation de zoom
                self.zoom_en_cours = True
                self.zoom_direction = 1
                self.zoom_animation = 0
                return None
        
        return None
    
    def changer_univers(self, direction):
        """Change d'univers avec animation de swipe"""
        nouvel_univers = self.univers_actuel + direction
        if 0 <= nouvel_univers < len(self.univers):
            self.transition_univers = True
            self.camera_cible_x = nouvel_univers * LARGEUR_ECRAN
    
    def gerer_clic_planete(self, pos):
        """Gère les clics sur la vue planète"""
        # Calcul du premier niveau de cette planète (global)
        premier_niveau = self.univers_actuel * self.nombre_planetes_par_univers * self.niveaux_par_planete + self.planete_selectionnee * self.niveaux_par_planete + 1
        
        for i, (px, py) in enumerate(self.plaques_positions):
            numero = premier_niveau + i
            est_debloque = numero <= self.niveau_max_debloque
            
            rect = pygame.Rect(px - 35, py - 20, 70, 40)
            if rect.collidepoint(pos) and est_debloque:
                self.son_select.play()

                # Niveau pas encore sorti = afficher une alerte
                if numero > NIVEAUX_DISPONIBLES:
                    if self.alerte is not None:
                        self.alerte.afficher("Niveau bientot disponible !")
                    return None

                # Si le mage est déjà sur cette plaque, lancer directement
                if i == self.mage_niveau_actuel:
                    self.niveau_cible = numero
                    self.portail_actif = True
                    self.portail_x = self.mage_x
                    self.portail_y = self.mage_y
                    self.portail_animation = 0
                    self.teleportation_en_cours = True
                else:
                    # Construire le chemin de plaques à parcourir
                    self.chemin_plaques = self.construire_chemin(self.mage_niveau_actuel, i)
                    self.plaque_courante_index = 0
                    
                    # Démarrer vers la première plaque du chemin
                    if self.chemin_plaques:
                        first_plaque = self.chemin_plaques[0]
                        self.mage_cible_x, self.mage_cible_y = self.plaques_positions[first_plaque]
                        # Mettre à jour la direction initiale
                        dx = self.mage_cible_x - self.mage_x
                        if dx > 0:
                            self.mage_direction = 1
                        else:
                            self.mage_direction = -1
                        
                        # initialiser le saut
                        self.mage_en_saut = True
                        self.mage_saut_progression = 0
                        self.mage_saut_start_x = self.mage_x
                        self.mage_saut_start_y = self.mage_y
                    
                    self.mage_en_mouvement = True
                    self.mage_niveau_actuel = i
                    self.niveau_cible = numero
                
                return None
        
        return None
    
    def construire_chemin(self, depart, arrivee):
        """Construit le chemin de plaques entre deux positions"""
        chemin = []
        if depart < arrivee:
            # Aller vers la droite (plaques croissantes)
            for i in range(depart + 1, arrivee + 1):
                chemin.append(i)
        else:
            # Aller vers la gauche (plaques décroissantes)
            for i in range(depart - 1, arrivee - 1, -1):
                chemin.append(i)
        return chemin
    
    def preparer_retour_niveau(self, numero_niveau):
        """Prépare l'animation de retour depuis un niveau"""
        # Recharger la config (niveau débloqué, pièces, etc.)
        self.recharger_donnees()
        # Calculer l'univers, la planète et la plaque
        niveaux_par_univers = self.nombre_planetes_par_univers * self.niveaux_par_planete
        univers_index = (numero_niveau - 1) // niveaux_par_univers
        niveau_dans_univers = (numero_niveau - 1) % niveaux_par_univers
        planete_index = niveau_dans_univers // self.niveaux_par_planete
        plaque_index = niveau_dans_univers % self.niveaux_par_planete
        
        self.univers_actuel = univers_index
        self.planetes = self.univers[self.univers_actuel]["planetes"]
        self.planete_selectionnee = planete_index
        self.mage_niveau_actuel = plaque_index
        self.mage_x, self.mage_y = self.plaques_positions[plaque_index]
        
        # Mettre à jour la position de la caméra pour l'univers
        self.camera_x = univers_index * LARGEUR_ECRAN
        self.camera_cible_x = self.camera_x
        
        # Activer l'animation de portail d'arrivée
        self.portail_actif = True
        self.portail_x = self.mage_x
        self.portail_y = self.mage_y
        self.portail_animation = 0
        self.mage_visible = False
        self.teleportation_en_cours = False  # C'est une arrivée
        self.retour_niveau = True
        self.etat_menu = "planete"
    
    def verifier_niveau_a_lancer(self):
        """Vérifie si un niveau doit être lancé (appelé chaque frame)"""
        if self.niveau_a_lancer is not None:
            niveau = self.niveau_a_lancer
            self.niveau_a_lancer = None
            return niveau
        return None
