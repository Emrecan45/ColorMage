import pygame
import sys
import os
import random
import math
from core.i18n import t
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, COULEURS, COULEUR_BOUTON, COULEUR_SURVOL, COULEUR_BORDURE, NIVEAUX_DISPONIBLES, resource_path
from core.config_manager import ConfigManager
from ui.chronometre import Chronometre
from ui.profil import Profil
from ui.parametres import Parametres

class Popup:
    """Gère l'affichage des popups de victoire et de défaite"""

    def __init__(self, gestionnaire_config=None):
        self.font = pygame.font.Font(None, 48)
        self.font_niveau = pygame.font.Font(None, 35)  # Pour afficher le niveau
        
        # son des clics
        if gestionnaire_config is None:
            self.gestionnaire_config = ConfigManager()
        else:
            self.gestionnaire_config = gestionnaire_config
        self.son_select = pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "select.wav")))
        
        # Sons de portail (changement de couleur) pour clic sur nouvelle planète
        self.sons_portail = [
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change1.wav"))),
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change2.wav"))),
            pygame.mixer.Sound(resource_path(os.path.join("assets/audio", "color_change3.wav")))
        ]
        
        # Configuration des planètes (doit correspondre à menu_niveaux)
        self.niveaux_par_planete = 5
        self.planetes_par_univers = 4
        self.niveaux_par_univers = self.niveaux_par_planete * self.planetes_par_univers  # 20 niveaux par univers
        
        # Noms des univers et planètes (doit correspondre à menu_niveaux)
        self.univers = [
            {"nom": "Royaume Nord", "planetes": ["Terra", "Pyros", "Aquaris", "Nebula"]},
            {"nom": "Royaume Sud", "planetes": ["Cryon", "Solara", "Vortex", "Obscura"]}
        ]
        
        self.largeur_popup = 600
        self.hauteur_popup = 450

        # Charger les images des mobs pour le grimoire
        ennemy_path = resource_path(os.path.join("assets/img/entities", "ennemy.png"))
        self.ennemy_sheet = pygame.image.load(ennemy_path)
        sprite_w = 192
        sprite_h = 192
        
        # Sorcier
        sorcier_rect = pygame.Rect(0, 0, sprite_w, sprite_h)
        self.img_sorcier = pygame.transform.scale(self.ennemy_sheet.subsurface(sorcier_rect), (100, 100))
        
        # Squelette
        squelette_rect = pygame.Rect(sprite_w, 4 * sprite_h, sprite_w, sprite_h)
        self.img_squelette = pygame.transform.scale(self.ennemy_sheet.subsurface(squelette_rect), (100, 100))
        
        # Slime vert
        slime_vert_sheet = pygame.image.load(resource_path(os.path.join("assets/img/entities", "slime_vert.png")))
        slime_vert_rect = pygame.Rect(0, 24, 24, 24)
        self.img_slime = pygame.transform.scale(slime_vert_sheet.subsurface(slime_vert_rect), (80, 80))
        
        # Slime violet
        slime_violet_sheet = pygame.image.load(resource_path(os.path.join("assets/img/entities", "slime_violet.png")))
        slime_violet_rect = pygame.Rect(0, 24, 24, 24)
        self.img_slime_violet = pygame.transform.scale(slime_violet_sheet.subsurface(slime_violet_rect), (80, 80))

        # Pyrolord et Cristal
        pyro_sheet = pygame.image.load(resource_path(os.path.join("assets/img/entities", "pyrolord.png"))).convert_alpha()
        slime_feu_cell = pyro_sheet.subsurface(pygame.Rect(0, 0, 288, 160))
        bbox = slime_feu_cell.get_bounding_rect()
        crop = slime_feu_cell.subsurface(bbox)
        ratio = 95 / crop.get_height()
        self.img_slime_feu = pygame.transform.scale(crop, (max(1, int(crop.get_width() * ratio)), 95))

        cristal_sheet = pygame.image.load(resource_path(os.path.join("assets/img/items", "cristal_feu.png"))).convert()
        cristal_sheet.set_colorkey((0, 0, 0))
        frame_rect = pygame.Rect(22, 151, 113 - 22 + 1, 88)
        frame = cristal_sheet.subsurface(frame_rect)
        cristal_frame = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        cristal_frame.blit(frame, (0, 0))
        bbox = cristal_frame.get_bounding_rect()
        if bbox.w > 0 and bbox.h > 0:
            cristal_frame = cristal_frame.subsurface(bbox).copy()
        ratio_cristal = 95 / cristal_frame.get_height()
        self.img_cristal = pygame.transform.scale(cristal_frame, (max(1, int(cristal_frame.get_width() * ratio_cristal)), 95))

        # Icône de pièce
        piece_sheet = pygame.image.load(resource_path(os.path.join("assets/img/items", "piece.png"))).convert_alpha()
        self.img_piece = pygame.transform.scale(piece_sheet.subsurface(pygame.Rect(0, 0, 16, 16)), (32, 32))


        # Taille illustrations grimoire
        taille_illu = 70

        # Bloc rouge
        self.img_bloc_rouge = pygame.Surface((taille_illu, taille_illu), pygame.SRCALPHA)
        pygame.draw.rect(self.img_bloc_rouge, COULEURS.get("rouge"), (0, 0, taille_illu, taille_illu))

       # Bloc mobile (plateforme mobile)
        self.img_bloc_bleu = pygame.Surface((taille_illu * 2, taille_illu * 2 // 2), pygame.SRCALPHA)
        pygame.draw.rect(self.img_bloc_bleu, COULEURS.get("bleu"), (0, 0, taille_illu * 2, taille_illu * 2 // 2))

        # Effet de mouvement pour bloc mobile
        effet_path = resource_path(os.path.join("assets/img/entities", "mouvement_effet.png"))
        img_effet = pygame.image.load(effet_path).convert_alpha()
        target_h = taille_illu * 2
        target_w = int(img_effet.get_width() * (target_h / img_effet.get_height()))
        largeur_surface = self.img_bloc_bleu.get_width() + target_w - 20
        hauteur_surface = max(taille_illu * 2, target_h)
        self.img_mobile_bleu = pygame.Surface((largeur_surface, hauteur_surface), pygame.SRCALPHA)

        x_off = 0
        y_off = (hauteur_surface - self.img_bloc_bleu.get_height()) // 2
        self.img_mobile_bleu.blit(self.img_bloc_bleu, (x_off, y_off))

        img_effet = pygame.transform.smoothscale(img_effet, (target_w, target_h))
        x_effet = self.img_bloc_bleu.get_width() - 20
        y_effet = (hauteur_surface - target_h) // 2
        self.img_mobile_bleu.blit(img_effet, (x_effet, y_effet))

        # Potion
        potion_path = resource_path(os.path.join("assets", "img", "items", "change_rouge.png"))
        self.img_potion = pygame.image.load(potion_path).convert_alpha()
        self.img_potion = pygame.transform.smoothscale(self.img_potion, (taille_illu, taille_illu))

        # Pic
        self.img_pic_tuto = pygame.image.load(resource_path(os.path.join("assets", "img", "items", "pic.png")))
        self.img_pic_tuto = pygame.transform.scale(self.img_pic_tuto, (taille_illu, taille_illu))

        # Porte
        self.img_porte_tuto = pygame.image.load(resource_path(os.path.join("assets", "img", "items", "porte.png")))
        self.img_porte_tuto = pygame.transform.scale(self.img_porte_tuto, (taille_illu, taille_illu))

        # Feu
        feu_sheet = pygame.image.load(resource_path(os.path.join("assets", "img", "items", "feu.png"))).convert_alpha()
        feu_fw = feu_sheet.get_width() // 8
        feu_frame = feu_sheet.subsurface(pygame.Rect(3 * feu_fw, 0, feu_fw, feu_sheet.get_height())).copy()
        bbox = feu_frame.get_bounding_rect()
        if bbox.w > 0 and bbox.h > 0:
            feu_frame = feu_frame.subsurface(bbox).copy()
        ratio_feu = 95 / feu_frame.get_height()
        self.img_feu = pygame.transform.scale(feu_frame, (max(1, int(feu_frame.get_width() * ratio_feu)), 95))

        # Démon
        demon_sheet = pygame.image.load(resource_path(os.path.join("assets", "img", "entities", "demon_idle.png"))).convert_alpha()
        demon_fw = demon_sheet.get_width() // 4
        demon_frame = demon_sheet.subsurface(pygame.Rect(0, 0, demon_fw, demon_sheet.get_height())).copy()
        bbox = demon_frame.get_bounding_rect()
        if bbox.w > 0 and bbox.h > 0:
            demon_frame = demon_frame.subsurface(bbox).copy()
        ratio_demon = 95 / demon_frame.get_height()
        self.img_demon = pygame.transform.scale(demon_frame, (max(1, int(demon_frame.get_width() * ratio_demon)), 95))

        # pages du grimoire (par niveau)
        self.grimoires = {
            1: {
                "titre": t("popup.bases"),
                "images": [self.img_potion, self.img_bloc_rouge, self.img_pic_tuto, self.img_porte_tuto],
                "lore": t("popup.bases_lore"),
                "lignes": t("popup.bases_tuto")
            },
            2: {
                "titre": t("popup.blocs"),
                "images": [self.img_mobile_bleu],
                "lore": t("popup.blocs_lore"),
                "lignes": t("popup.blocs_tuto")
            },
            3: {
                "titre": t("popup.sorcier"),
                "images": [self.img_sorcier],
                "lore": t("popup.sorcier_lore"),
                "lignes": t("popup.sorcier_tuto")
            },
            4: {
                "titre": t("popup.garde"),
                "images": [self.img_squelette],
                "lore": t("popup.garde_lore"),
                "lignes": t("popup.garde_tuto")
            },
            5: {
                "titre": t("popup.slimes"),
                "images": [self.img_slime, self.img_slime_violet],
                "lore": t("popup.slimes_lore"),
                "lignes": t("popup.slimes_tuto")
            },
            6: {
                "titre": t("popup.cristal"),
                "images": [self.img_cristal],
                "lore": t("popup.cristal_lore"),
                "lignes": t("popup.cristal_tuto")
            },
            7: {
                "titre": t("popup.brasier"),
                "images": [self.img_feu],
                "lore": t("popup.brasier_lore"),
                "lignes": t("popup.brasier_tuto")
            },
            8: {
                "titre": t("popup.butin"),
                "images": [self.img_piece, self.img_potion, self.img_cristal],
                "lore": t("popup.butin_lore"),
                "lignes": t("popup.butin_tuto")
            },
            9: {
                "titre": t("popup.demon"),
                "images": [self.img_demon],
                "lore": t("popup.demon_lore"),
                "lignes": t("popup.demon_tuto")
            },
            10: {
                "titre": t("popup.pyrolord"),
                "images": [self.img_slime_feu],
                "lore": "Un petit slime de braise sautille au fond de l'antre. "
                        "Il a l'air inoffensif... vraiment ?",
                "lignes": t("popup.pyrolord_lore2")
            }
        }
        
        # Rectangle du popup
        self.popup_rect = pygame.Rect((LARGEUR_ECRAN - self.largeur_popup) // 2, (HAUTEUR_ECRAN - self.hauteur_popup) // 2, self.largeur_popup, self.hauteur_popup)
        
        # Créer les boutons (positionnés verticalement)
        self.bouton_suivant = pygame.Rect(0, 0, 260, 60)
        self.bouton_suivant.center = (self.popup_rect.centerx, self.popup_rect.top + 160)
        
        self.bouton_recommencer = pygame.Rect(0, 0, 260, 60)
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 250)
        
        self.bouton_quitter = pygame.Rect(0, 0, 260, 60)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 340)

        # Fond
        self.etoiles = []
        for i in range(150):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, HAUTEUR_ECRAN)
            taille = random.randint(1, 3)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            self.etoiles.append([x, y, taille, brillance, vitesse_scintillement, random.uniform(0, 2 * math.pi)])
        self.temps_global = 0

    def maj_volume(self):
        """Met à jour le volume du son de sélection"""
        volumes = self.gestionnaire_config.volumes
        volume = volumes.get("effets", 50) / 100
        self.son_select.set_volume(volume)
        for son in self.sons_portail:
            son.set_volume(volume)

    def dessiner_etoiles(self, ecran):
        """Dessine les étoiles scintillantes"""
        for etoile in self.etoiles:
            x, y, taille, brillance_base, vitesse, phase = etoile
            # Scintillement
            brillance = int(brillance_base * (0.5 + 0.5 * math.sin(self.temps_global * vitesse + phase)))
            brillance = max(50, min(255, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (x, y), taille)

    def niveau_existe(self, numero_niveau):
        """Vérifie si un niveau est disponible (sorti et fichier présent)."""
        if numero_niveau > NIVEAUX_DISPONIBLES:
            return False
        planetes = ["terra", "pyros", "aquaris", "nebula", "cryon", "solara", "vortex", "obscura"]
        planete_idx = (numero_niveau - 1) // 5
        if planete_idx < len(planetes):
            planete = planetes[planete_idx]
        else:
            planete = "terra"
        chemin = resource_path(os.path.join("levels", planete, "niveau_" + str(numero_niveau) + ".json"))
        try:
            with open(chemin, "r") as f:
                pass
            return True
        except:
            return False

    def est_dernier_niveau_planete(self, niveau):
        """Vérifie si c'est le dernier niveau d'une planète"""
        return niveau % self.niveaux_par_planete == 0
    
    def est_dernier_niveau_univers(self, niveau):
        """Vérifie si c'est le dernier niveau d'un univers"""
        return niveau % self.niveaux_par_univers == 0
    
    def obtenir_univers_actuel(self, niveau):
        """Retourne l'index de l'univers pour un niveau donné"""
        return (niveau - 1) // self.niveaux_par_univers
    
    def obtenir_planete_dans_univers(self, niveau):
        """Retourne l'index de la planète dans son univers pour un niveau donné"""
        niveau_dans_univers = (niveau - 1) % self.niveaux_par_univers
        return niveau_dans_univers // self.niveaux_par_planete
    
    def gerer_clic_victoire(self, pos, niveau_actuel):
        """Gère les clics pour le popup de victoire
        
        Args:
            pos: Position du clic (x, y)
            niveau_actuel: Numéro du niveau actuel
            
        Returns:
            str: "suivant", "planete_suivante", "univers_suivant", "rejouer", "quitter" ou None
        """
        # Vérifier si le niveau suivant existe pour activer le bouton
        if self.niveau_existe(niveau_actuel + 1):
            if self.bouton_suivant.collidepoint(pos):
                # Si c'est le dernier niveau de l'univers
                if self.est_dernier_niveau_univers(niveau_actuel):
                    random.choice(self.sons_portail).play()
                    return "univers_suivant"
                # Si c'est le dernier niveau de la planète
                elif self.est_dernier_niveau_planete(niveau_actuel):
                    random.choice(self.sons_portail).play()
                    return "planete_suivante"
                else:
                    self.maj_volume()
                    self.son_select.play()
                    return "suivant"
        
        if self.bouton_recommencer.collidepoint(pos):
            self.maj_volume()
            self.son_select.play()
            return "rejouer"

        elif self.bouton_quitter.collidepoint(pos):
            self.maj_volume()
            self.son_select.play()
            return "quitter"
        return None
    
    def gerer_clic_defaite(self, pos):
        """Gère les clics pour le popup de défaite
        
        Args:
            pos: Position du clic (x, y)
            
        Returns:
            str: "rejouer", "quitter" ou None
        """
        if self.bouton_recommencer.collidepoint(pos):
            self.maj_volume()
            self.son_select.play()
            return "rejouer"
        elif self.bouton_quitter.collidepoint(pos):
            self.maj_volume()
            self.son_select.play()
            return "quitter"
        return None

    def afficher_popup_grimoire(self, ecran, numero_niveau, draw_background=None, alerte=None):
        """Affiche un popup grimoire pour un niveau donné
        Freeze jusqu'à ce que le joueur clique OK.
        """
        if numero_niveau not in self.grimoires:
            return
        
        grimoire = self.grimoires[numero_niveau]
        titre = grimoire["titre"]
        images = self.redimensionner_images_grimoire(grimoire["images"], 95)
        lignes = grimoire["lignes"]
        
        # Dimensions du popup
        popup_largeur = 700
        popup_hauteur = 400
        popup_rect = pygame.Rect((LARGEUR_ECRAN - popup_largeur) // 2, (HAUTEUR_ECRAN - popup_hauteur) // 2, popup_largeur, popup_hauteur)
        
        # Bouton OK
        bouton_ok = pygame.Rect(0, 0, 180, 50)
        bouton_ok.center = (popup_rect.centerx, popup_rect.bottom - 50)
        
        # Fonts
        font_titre = pygame.font.Font(None, 46)
        font_texte = pygame.font.Font(None, 32)
        font_bouton = pygame.font.Font(None, 40)
        
        self.maj_volume()
        
        # Fond du jeu
        fond_capture = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        fond_capture.blit(ecran, (0, 0))
        
        while True:
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_RETURN or evenement.key == pygame.K_SPACE:
                        self.son_select.play()
                        return
                elif evenement.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_ok.collidepoint(evenement.pos):
                        self.son_select.play()
                        return
            
            # Fond
            ecran.blit(fond_capture, (0, 0))
            
            # Overlay semi-transparent
            overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            ecran.blit(overlay, (0, 0))
            
            # Popup fond
            pygame.draw.rect(ecran, (40, 40, 65), popup_rect, border_radius=15)
            pygame.draw.rect(ecran, (255, 215, 0), popup_rect, 3, border_radius=15)
            
            # Titre
            titre_surface = font_titre.render(titre, True, (255, 215, 0))
            ecran.blit(titre_surface, (popup_rect.centerx - titre_surface.get_width() // 2, popup_rect.top + 20))
            
            # Images des mobs
            total_largeur_images = 0
            for img in images:
                total_largeur_images = total_largeur_images + img.get_width()
            total_largeur_images = total_largeur_images + (len(images) - 1) * 15

            max_hauteur_img = 0
            for img in images:
                if img.get_height() > max_hauteur_img:
                    max_hauteur_img = img.get_height()

            x_depart_images = popup_rect.centerx - total_largeur_images // 2
            y_images = popup_rect.top + 70

            decalage_x = 0
            for img in images:
                # Centrer verticalement chaque image
                decalage_y = (max_hauteur_img - img.get_height()) // 2
                ecran.blit(img, (x_depart_images + decalage_x, y_images + decalage_y))
                decalage_x = decalage_x + img.get_width() + 15
            
            # Lignes de texte
            texte_y = y_images + max_hauteur_img + 20
            

            for idx in range(len(lignes)):
                ligne = lignes[idx]
                texte_surface = font_texte.render(ligne, True, (255, 255, 255))
                ecran.blit(texte_surface, (popup_rect.centerx - texte_surface.get_width() // 2, texte_y + idx * 32))
            
            # Bouton OK
            souris = pygame.mouse.get_pos()
            if bouton_ok.collidepoint(souris):
                pygame.draw.rect(ecran, (80, 160, 80), bouton_ok, border_radius=10)
            else:
                pygame.draw.rect(ecran, (50, 130, 50), bouton_ok, border_radius=10)
            pygame.draw.rect(ecran, (255, 255, 255), bouton_ok, 2, border_radius=10)
            ok_surface = font_bouton.render("C'est parti !", True, (255, 255, 255))
            ecran.blit(ok_surface, (bouton_ok.centerx - ok_surface.get_width() // 2, bouton_ok.centery - ok_surface.get_height() // 2))
            if alerte:
                alerte.dessiner(ecran)
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def creer_silhouette(self, image):
        """Crée une silhouette noire à l'image"""
        largeur = image.get_width()
        hauteur = image.get_height()
        silhouette = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        silhouette.blit(image, (0, 0))
        # Parcourir chaque pixel et le rendre noir tout en gardant la transparence
        for px in range(largeur):
            for py in range(hauteur):
                r, g, b, a = silhouette.get_at((px, py))
                if a > 0:
                    silhouette.set_at((px, py), (20, 20, 30, a))
        return silhouette

    def redimensionner_images_grimoire(self, images, hauteur_cible):
        """Redimensionne les images d'une page de grimoire."""
        resultat = []
        for img in images:
            if img is self.img_cristal:
                h = 70
            elif img is self.img_piece:
                h = 70
            else:
                h = hauteur_cible
            if img.get_height() == 0:
                w = h
            else:
                w = int(img.get_width() * (h / img.get_height()))
            resultat.append(pygame.transform.smoothscale(img, (w, h)))
        return resultat

    def afficher_grimoire_complet(self, ecran, alerte=None):
        """Affiche le grimoire complet et les infos non débloqués apparaissent en silhouette noire hehe"""
        # Collecter tous les pages disponibles
        numeros = list(self.grimoires.keys())
        numeros.sort()
        # Récupérer le niveau le plus haut débloqué par le joueur
        niveau_joueur = self.gestionnaire_config.obtenir_niveau_actuel()
        page_idx = 0
        
        font_titre = pygame.font.Font(None, 64)
        font_page = pygame.font.Font(None, 46)
        font_texte = pygame.font.Font(None, 32)
        font_bouton = pygame.font.Font(None, 38)
        font_nav = pygame.font.Font(None, 44)
        
        popup_largeur = LARGEUR_ECRAN - 120
        popup_hauteur = HAUTEUR_ECRAN - 120
        popup_rect = pygame.Rect((LARGEUR_ECRAN - popup_largeur) // 2, (HAUTEUR_ECRAN - popup_hauteur) // 2, popup_largeur, popup_hauteur)

        # Bouton Fermer
        bouton_fermer = pygame.Rect(0, 0, 250, 50)
        bouton_fermer.center = (popup_rect.centerx, popup_rect.bottom - 40)

        # Flèches de navigation
        arrow_h = bouton_fermer.height
        arrow_w = 50
        spacing = 20
        bouton_prec = pygame.Rect(0, 0, arrow_w, arrow_h)
        bouton_suiv = pygame.Rect(0, 0, arrow_w, arrow_h)
        bouton_prec.center = (bouton_fermer.left - spacing - arrow_w // 2, bouton_fermer.centery)
        bouton_suiv.center = (bouton_fermer.right + spacing + arrow_w // 2, bouton_fermer.centery)
        
        self.maj_volume()
        
        while True:
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_ESCAPE:
                        self.son_select.play()
                        return
                    elif evenement.key == pygame.K_LEFT and page_idx > 0:
                        page_idx = page_idx - 1
                    elif evenement.key == pygame.K_RIGHT and page_idx < len(numeros) - 1:
                        page_idx = page_idx + 1
                elif evenement.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_fermer.collidepoint(evenement.pos):
                        self.son_select.play()
                        return
                    if bouton_prec.collidepoint(evenement.pos) and page_idx > 0:
                        self.son_select.play()
                        page_idx = page_idx - 1
                    if bouton_suiv.collidepoint(evenement.pos) and page_idx < len(numeros) - 1:
                        self.son_select.play()
                        page_idx = page_idx + 1
            
            # Fond étoilé
            self.temps_global = self.temps_global + 1
            ecran.fill((10, 10, 30))
            self.dessiner_etoiles(ecran)
            
            titre_gen = font_titre.render(t("popup.grimoire"), True, (255, 215, 0))
            ecran.blit(titre_gen, (popup_rect.centerx - titre_gen.get_width() // 2, popup_rect.top + 12))
            
            # Page courante
            numero = numeros[page_idx]
            grimoire = self.grimoires[numero]
            est_debloque = numero <= niveau_joueur
            
            if est_debloque:
                # soustitre de la page
                sous_titre_text = grimoire["titre"]
                sous_titre = font_page.render(sous_titre_text, True, (255, 255, 255))
                ecran.blit(sous_titre, (popup_rect.centerx - sous_titre.get_width() // 2, popup_rect.top + 110))
                
                # Image
                images = grimoire["images"]
                if numero in (3, 4, 5):
                    hauteur_cible = 160
                elif numero == 2:
                    hauteur_cible = 170
                else:
                    hauteur_cible = 110
                images_redimensionnees = self.redimensionner_images_grimoire(images, hauteur_cible)

                ecart_images = 45
                total_largeur_images = sum(i.get_width() for i in images_redimensionnees) + (len(images_redimensionnees) - 1) * ecart_images
                x_depart_images = popup_rect.centerx - total_largeur_images // 2

                zone_img_haut = popup_rect.top + 160
                zone_img_hauteur = 160
                # Aligner les images par le bas
                max_h = 0
                for im in images_redimensionnees:
                    if im.get_height() > max_h:
                        max_h = im.get_height()
                bas_ligne = zone_img_haut + (zone_img_hauteur + max_h) // 2
                decalage_x = 0
                bas_cristal = zone_img_haut + (zone_img_hauteur + hauteur_cible) // 2
                for i in range(len(images_redimensionnees)):
                    img = images_redimensionnees[i]
                    if images[i] is self.img_cristal:
                        y_img = bas_cristal - img.get_height() - 12
                    else:
                        y_img = bas_ligne - img.get_height()
                    ecran.blit(img, (x_depart_images + decalage_x, y_img))
                    decalage_x = decalage_x + img.get_width() + ecart_images

                # Texte
                texte_y = zone_img_haut + zone_img_hauteur + 20
                max_w = popup_rect.width - 120
                if "lore" in grimoire:
                    # afficher lore
                    s = font_texte.render(grimoire["lore"], True, (200, 200, 200))
                    ecran.blit(s, (popup_rect.centerx - s.get_width() // 2, texte_y))
                    texte_y = texte_y + font_texte.get_linesize() + 30

                for idx in range(len(grimoire["lignes"])):
                    ligne = grimoire["lignes"][idx]
                    txt_rendu = font_texte.render(ligne, True, (220, 220, 220))
                    ecran.blit(txt_rendu, (popup_rect.centerx - txt_rendu.get_width() // 2, texte_y + idx * 32))
            else:
                # Titre mystere
                sous_titre = font_page.render(t("popup.mystere"), True, (100, 100, 120))
                ecran.blit(sous_titre, (popup_rect.centerx - sous_titre.get_width() // 2, popup_rect.top + 110))
                
                # Images sous ombre noire
                images = grimoire["images"]
                if numero in (3, 4, 5):
                    hauteur_cible = 160
                elif numero == 2:
                    hauteur_cible = 170
                else:
                    hauteur_cible = 110
                images_redimensionnees = self.redimensionner_images_grimoire(images, hauteur_cible)

                ecart_images = 45
                total_largeur_images = sum(i.get_width() for i in images_redimensionnees) + (len(images_redimensionnees) - 1) * ecart_images
                x_depart_images = popup_rect.centerx - total_largeur_images // 2
                zone_img_haut = popup_rect.top + 160
                zone_img_hauteur = 160
                # Aligner les images par le bas
                max_h = 0
                for im in images_redimensionnees:
                    if im.get_height() > max_h:
                        max_h = im.get_height()
                bas_ligne = zone_img_haut + (zone_img_hauteur + max_h) // 2
                decalage_x = 0
                for img in images_redimensionnees:
                    sil = self.creer_silhouette(img)
                    y_img = bas_ligne - img.get_height()
                    ecran.blit(sil, (x_depart_images + decalage_x, y_img))
                    decalage_x = decalage_x + img.get_width() + ecart_images
                # Icône cadenas
                cadenas_path = resource_path(os.path.join("assets", "img", "ui", "cadena.png"))
                font_cadenas = pygame.font.Font(None, 36)
                texte_cadenas = font_cadenas.render(t("popup.cadenas"), True, (120, 120, 140))
                if os.path.exists(cadenas_path):
                    cadenas_img = pygame.image.load(cadenas_path).convert_alpha()
                    taille_cadenas = 40
                    cadenas_img = pygame.transform.smoothscale(cadenas_img, (taille_cadenas, taille_cadenas))
                    lock_x = popup_rect.centerx - taille_cadenas // 2
                    lock_y = zone_img_haut + (zone_img_hauteur // 2) - taille_cadenas // 2
                    ecran.blit(cadenas_img, (lock_x, lock_y))
                    haut_zone = zone_img_haut + zone_img_hauteur
                    pos_y_texte = haut_zone + 80
                    ecran.blit(texte_cadenas, (popup_rect.centerx - texte_cadenas.get_width() // 2, pos_y_texte))
                else:
                    haut_zone = zone_img_haut + zone_img_hauteur
                    pos_y_texte = haut_zone + 80
                    ecran.blit(texte_cadenas, (popup_rect.centerx - texte_cadenas.get_width() // 2, pos_y_texte))
            
            # Navigation
            souris = pygame.mouse.get_pos()
            
            # Bouton précédent
            font_button = pygame.font.SysFont(None, 50)
            if page_idx > 0:
                if bouton_prec.collidepoint(souris):
                    couleur_prec = COULEUR_SURVOL
                else:
                    couleur_prec = COULEUR_BOUTON
                pygame.draw.rect(ecran, couleur_prec, bouton_prec, border_radius=10)
                pygame.draw.rect(ecran, COULEUR_BORDURE, bouton_prec, 3, border_radius=10)
                prec_txt = font_nav.render("<", True, (255, 255, 255))
                ecran.blit(prec_txt, (bouton_prec.centerx - prec_txt.get_width() // 2, bouton_prec.centery - prec_txt.get_height() // 2))
            # Bouton suivant
            if page_idx < len(numeros) - 1:
                if bouton_suiv.collidepoint(souris):
                    couleur_suiv = COULEUR_SURVOL
                else:
                    couleur_suiv = COULEUR_BOUTON
                pygame.draw.rect(ecran, couleur_suiv, bouton_suiv, border_radius=10)
                pygame.draw.rect(ecran, COULEUR_BORDURE, bouton_suiv, 3, border_radius=10)
                suiv_txt = font_nav.render(">", True, (255, 255, 255))
                ecran.blit(suiv_txt, (bouton_suiv.centerx - suiv_txt.get_width() // 2, bouton_suiv.centery - suiv_txt.get_height() // 2))
            
            
            # Bouton fermer 
            if bouton_fermer.collidepoint(souris):
                couleur_fermer = (150, 60, 60)
            else:
                couleur_fermer = (120, 40, 40)
            pygame.draw.rect(ecran, couleur_fermer, bouton_fermer, border_radius=10)
            pygame.draw.rect(ecran, COULEUR_BORDURE, bouton_fermer, 3, border_radius=10)
            fermer_txt = font_button.render(t("popup.fermer"), True, (255, 255, 255))
            ecran.blit(fermer_txt, (bouton_fermer.centerx - fermer_txt.get_width() // 2, bouton_fermer.centery - fermer_txt.get_height() // 2))
            if alerte:
                alerte.dessiner(ecran)
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def dessiner_popup_victoire(self, ecran, niveau_actuel, temps_ms=0, est_record=False, pieces_gagnees=0):
        """Dessine le popup de victoire avec le temps et indication de record

        Args:
            ecran: Surface pygame
            niveau_actuel: Numéro du niveau
            temps_ms: Temps réalisé en millisecondes
            est_record: True si c'est un nouveau record
            pieces_gagnees: Nombre de pièces collectées pendant ce niveau
        """
        self.maj_volume()
        
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)

        # Titre
        titre_surface = self.font.render(t("popup.bravo"), True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 40
        ecran.blit(titre_surface, (titre_x, titre_y))
        
        # Afficher le niveau actuel sous le titre
        planete = ((niveau_actuel - 1) // 5) + 1
        niveau_planete = ((niveau_actuel - 1) % 5) + 1
        noms_planetes = ["Terra", "Pyros", "Aquaris", "Nebula", "Cryon", "Solara", "Vortex", "Obscura"]
        if planete <= len(noms_planetes):
            nom_planete = noms_planetes[planete - 1]
        else:
            nom_planete = f"Planète {planete}"
        
        niveau_texte = f"{t('pause.planete')} {nom_planete} - {t('pause.niv')} {niveau_actuel}"
        niveau_surface = self.font_niveau.render(niveau_texte, True, (100, 100, 100))
        niveau_x = self.popup_rect.x + (self.popup_rect.width - niveau_surface.get_width()) // 2
        niveau_y = self.popup_rect.y + 80
        ecran.blit(niveau_surface, (niveau_x, niveau_y))
        
        # Afficher le temps et les pièces gagnées
        font_temps = pygame.font.Font(None, 40)
        temps_y = self.popup_rect.y + 120

        temps_surface = None
        if temps_ms > 0:
            temps_texte = t("popup.temps") + Chronometre.formater_temps(self, temps_ms)
            temps_surface = font_temps.render(temps_texte, True, (0, 0, 0))

        # compteur de pièces
        pieces_surface = font_temps.render(str(pieces_gagnees), True, (0, 0, 0))

        espace = 30
        largeur_totale = 0
        if temps_surface:
            largeur_totale += temps_surface.get_width() + espace
        largeur_totale += self.img_piece.get_width() + 6 + pieces_surface.get_width()

        x = self.popup_rect.x + (self.popup_rect.width - largeur_totale) // 2
        if temps_surface:
            ecran.blit(temps_surface, (x, temps_y))
            x += temps_surface.get_width() + espace
        icone_y = temps_y + (pieces_surface.get_height() - self.img_piece.get_height()) // 2
        ecran.blit(self.img_piece, (x, icone_y))
        x += self.img_piece.get_width() + 6
        ecran.blit(pieces_surface, (x, temps_y))
        
        # Afficher "Nouveau record !" si c'est le cas
        if est_record:
            record_surface = self.font.render("Nouveau record !", True, (0, 180, 0))
            record_x = self.popup_rect.x + (self.popup_rect.width - record_surface.get_width()) // 2
            record_y = self.popup_rect.y + 145
            ecran.blit(record_surface, (record_x, record_y))

        # Liste des boutons avec leurs textes
        boutons = []
        
        # Ajuster les positions des boutons selon s'il y a un record ou non
        if est_record:
            # Décaler les boutons vers le bas si record affiché
            premier_bouton_y = 220
        else:
            premier_bouton_y = 180
        
        # Ajouter le bouton "Niveau suivant" ou nom de la planète/univers suivant seulement s'il existe
        texte_bouton_suivant = t("popup.niveau_suivant")
        couleur_planete = None
        
        if self.niveau_existe(niveau_actuel + 1):
            self.bouton_suivant.center = (self.popup_rect.centerx, self.popup_rect.top + premier_bouton_y)
            
            # Vérifier si c'est le dernier niveau de l'univers
            if self.est_dernier_niveau_univers(niveau_actuel):
                univers_actuel_idx = self.obtenir_univers_actuel(niveau_actuel)
                univers_suivant_idx = univers_actuel_idx + 1
                
                if univers_suivant_idx < len(self.univers):
                    nom_univers = self.univers[univers_suivant_idx]["nom"]
                    texte_bouton_suivant = nom_univers
                    couleur_planete = (255, 215, 0)  # Couleur or pour univers
                else:
                    texte_bouton_suivant = t("popup.suivant")
                    couleur_planete = (60, 180, 60)
            # Changer le texte si c'est le dernier niveau de la planète
            elif self.est_dernier_niveau_planete(niveau_actuel):
                # Calculer l'univers et la planète actuels
                univers_idx = self.obtenir_univers_actuel(niveau_actuel)
                planete_dans_univers = self.obtenir_planete_dans_univers(niveau_actuel)
                planete_suivante_idx = planete_dans_univers + 1
                
                if univers_idx < len(self.univers) and planete_suivante_idx < len(self.univers[univers_idx]["planetes"]):
                    nom_planete = self.univers[univers_idx]["planetes"][planete_suivante_idx]
                    texte_bouton_suivant = nom_planete
                    
                    # Couleurs des planètes par univers
                    couleurs_planetes = {
                        # Royaume Nord
                        "Terra": (100, 180, 100),
                        "Pyros": (200, 80, 60),
                        "Aquaris": (60, 120, 200),
                        "Nebula": (150, 80, 180),
                        # Royaume Sud
                        "Cryon": (150, 220, 255),
                        "Solara": (255, 180, 50),
                        "Vortex": (180, 180, 200),
                        "Obscura": (60, 40, 80)
                    }
                    couleur_planete = couleurs_planetes.get(nom_planete, (60, 180, 60))
                else:
                    texte_bouton_suivant = t("popup.suivant")
                    couleur_planete = (60, 180, 60)
            
            boutons.append((self.bouton_suivant, texte_bouton_suivant, couleur_planete))
            self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + premier_bouton_y + 90)
            self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + premier_bouton_y + 180)
        else:
            self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + premier_bouton_y)
            self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + premier_bouton_y + 90)
        
        boutons.append((self.bouton_recommencer, t("pause.recommencer"), None))
        boutons.append((self.bouton_quitter, t("pause.quitter"), None))

        # Dessiner les boutons
        for item in boutons:
            if len(item) == 3:
                rect, texte, couleur_planete = item
            else:
                rect, texte = item
                couleur_planete = None

            if couleur_planete:
                if rect.collidepoint(pygame.mouse.get_pos()):
                    couleur_survol = tuple(min(255, c + 30) for c in couleur_planete)
                    pygame.draw.rect(ecran, couleur_survol, rect, border_radius=10)
                else:
                    pygame.draw.rect(ecran, couleur_planete, rect, border_radius=10)
            else:
                # Effet de survol
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(ecran, (200, 200, 200), rect, border_radius=10)
                else:
                    pygame.draw.rect(ecran, (230, 230, 230), rect, border_radius=10)

            # Bordure du bouton
            pygame.draw.rect(ecran, (0, 0, 0), rect, 3, border_radius=10)

            # Texte du bouton
            texte_surface = self.font.render(texte, True, (0, 0, 0))
            texte_x = rect.x + (rect.width - texte_surface.get_width()) // 2
            texte_y = rect.y + (rect.height - texte_surface.get_height()) // 2
            ecran.blit(texte_surface, (texte_x, texte_y))

    def dessiner_popup_defaite(self, ecran, niveau_actuel=None):
        """Dessine le popup de défaite
        
        Args:
            ecran: Surface pygame
            niveau_actuel: Numéro du niveau actuel
        """
        self.maj_volume()
        
        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), self.popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), self.popup_rect, 4)

        # Titre
        titre_surface = self.font.render(t("popup.gameover"), True, (0, 0, 0))
        titre_x = self.popup_rect.x + (self.popup_rect.width - titre_surface.get_width()) // 2
        titre_y = self.popup_rect.y + 60
        ecran.blit(titre_surface, (titre_x, titre_y))
        
        # Afficher le niveau actuel sous le titre
        if niveau_actuel:
            planete = ((niveau_actuel - 1) // 5) + 1
            niveau_planete = ((niveau_actuel - 1) % 5) + 1
            noms_planetes = ["Terra", "Pyros", "Aquaris", "Nebula", "Cryon", "Solara", "Vortex", "Obscura"]
            if planete <= len(noms_planetes):
                nom_planete = noms_planetes[planete - 1]
            else:
                nom_planete = f"Planète {planete}"
            
            niveau_texte = f"{t('pause.planete')} {nom_planete} - {t('pause.niv')} {niveau_actuel}"
            niveau_surface = self.font_niveau.render(niveau_texte, True, (100, 100, 100))
            niveau_x = self.popup_rect.x + (self.popup_rect.width - niveau_surface.get_width()) // 2
            niveau_y = self.popup_rect.y + 110
            ecran.blit(niveau_surface, (niveau_x, niveau_y))

        # Ajuster les positions pour 2 boutons
        self.bouton_recommencer.center = (self.popup_rect.centerx, self.popup_rect.top + 210)
        self.bouton_quitter.center = (self.popup_rect.centerx, self.popup_rect.top + 300)

        # Liste des boutons avec leurs textes
        boutons = [
            (self.bouton_recommencer, t("pause.recommencer")),
            (self.bouton_quitter, t("pause.quitter"))
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

    def afficher_popup_confirmation_reset(self, ecran, parametres=None, type_reset="sauvegarde", alerte=None):
        """Affiche un popup de confirmation pour la réinitialisation
        
        Args:
            ecran: Surface pygame
            parametres: Objet Parametres ou Profil pour redessiner le fond
            type_reset: "sauvegarde" ou "parametres"
        
        Returns:
            str: "confirmer", "annuler" ou None
        """
        # Dimensions du popup de confirmation (plus grand)
        largeur_popup = 600
        hauteur_popup = 350
        popup_rect = pygame.Rect((LARGEUR_ECRAN - largeur_popup) // 2, (HAUTEUR_ECRAN - hauteur_popup) // 2, largeur_popup, hauteur_popup)
        
        # Boutons de confirmation (plus bas)
        bouton_confirmer = pygame.Rect(0, 0, 200, 55)
        bouton_confirmer.center = (popup_rect.centerx - 110, popup_rect.top + 270)
        
        bouton_annuler = pygame.Rect(0, 0, 200, 55)
        bouton_annuler.center = (popup_rect.centerx + 110, popup_rect.top + 270)
        
        # Messages selon le type de reset
        if type_reset == "import":
            lignes = [
                t("popup.import_titre"),
                t("popup.import_desc"),
                "",
                t("popup.import_warn")
            ]
        elif type_reset == "parametres":
            lignes = [
                t("popup.param_titre"),
                t("popup.param_desc"),
                "",
                t("popup.param_warn")
            ]
        else:
            lignes = [
                t("popup.reset_titre"),
                t("popup.reset_desc"),
                "",
                t("popup.reset_warn")
            ]
        
        # Mettre à jour le volume du son
        self.maj_volume()
        
        while True:
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                    return "annuler"
                elif evenement.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_confirmer.collidepoint(evenement.pos):
                        self.son_select.play()
                        return "confirmer"
                    elif bouton_annuler.collidepoint(evenement.pos):
                        self.son_select.play()
                        return "annuler"
            
            # Redessiner le fond (pour popup annuler ou confirmer)
            if parametres:
                # Vérifier si c'est Profil ou Parametres
                try:
                    parametres.afficher_profil(ecran)
                except Exception:
                    parametres.afficher_parametres(ecran)
            
            # Dessiner le fond légèrement grisé
            overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            ecran.blit(overlay, (0, 0))
            
            # Dessiner le popup
            pygame.draw.rect(ecran, (60, 60, 80), popup_rect, border_radius=15)
            pygame.draw.rect(ecran, (255, 255, 255), popup_rect, 3, border_radius=15)
            
            # Titre
            titre = pygame.font.Font(None, 40).render(t("popup.confirmation"), True, (255, 255, 255))
            ecran.blit(titre, (popup_rect.centerx - titre.get_width() // 2, popup_rect.top + 30))
            
            # Message
            font_message = pygame.font.Font(None, 30)
            
            for idx in range(len(lignes)):
                ligne = lignes[idx]
                text = font_message.render(ligne, True, (255, 255, 255))
                ecran.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 110 + idx * 35))
            
            # Boutons
            souris_pos = pygame.mouse.get_pos()
            
            # Bouton confirmer (rouge)
            if bouton_confirmer.collidepoint(souris_pos):
                pygame.draw.rect(ecran, (180, 60, 60), bouton_confirmer, border_radius=10)
            else:
                pygame.draw.rect(ecran, (150, 40, 40), bouton_confirmer, border_radius=10)
            pygame.draw.rect(ecran, (255, 255, 255), bouton_confirmer, 2, border_radius=10)
            
            # Bouton annuler (vert)
            if bouton_annuler.collidepoint(souris_pos):
                pygame.draw.rect(ecran, (60, 180, 60), bouton_annuler, border_radius=10)
            else:
                pygame.draw.rect(ecran, (40, 150, 40), bouton_annuler, border_radius=10)
            pygame.draw.rect(ecran, (255, 255, 255), bouton_annuler, 2, border_radius=10)
            
            # Textes des boutons
            confirmer_text = pygame.font.Font(None, 36).render(t("popup.confirmer"), True, (255, 255, 255))
            annuler_text = pygame.font.Font(None, 36).render(t("popup.annuler"), True, (255, 255, 255))
            
            ecran.blit(confirmer_text, (bouton_confirmer.centerx - confirmer_text.get_width() // 2, 
                                      bouton_confirmer.centery - confirmer_text.get_height() // 2))
            ecran.blit(annuler_text, (bouton_annuler.centerx - annuler_text.get_width() // 2, 
                                    bouton_annuler.centery - annuler_text.get_height() // 2))
            if alerte:
                alerte.dessiner(ecran)
            pygame.display.flip()
