import pygame
import json
import random
import math
import os
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS, LARGEUR_ECRAN, HAUTEUR_ECRAN
from enemies import Sorcier
from enemies import Squelette
from enemies import Slime
from enemies import Piece
from config_manager import ConfigManager

class PlateformeMobile:
    """Plateforme qui bouge horizontalement ou verticallement."""
    def __init__(self, cell_x, cell_y, dirv=1, range_blocks=1, sens=1, speed_px=1.0):
        self.cell_x = int(cell_x)
        self.cell_y = int(cell_y)
        self.dir = int(dirv)  # 1 = horizontal, -1 = vertical
        # s'assurer que les valeurs sont positives
        try:
            if range_blocks is not None:
                self.range_blocks = abs(int(range_blocks))
            else:
                self.range_blocks = 1
        except Exception:
            self.range_blocks = 1
        try:
            if speed_px is not None:
                self.vitesse = abs(float(speed_px))
            else:
                self.vitesse = 1.0
        except Exception:
            self.vitesse = 1.0
        
        # position d'origine
        self.origine_x = self.cell_x * TAILLE_CELLULE
        self.origine_y = self.cell_y * TAILLE_CELLULE
        
        # plage de déplacement
        self.plage = self.range_blocks * TAILLE_CELLULE
        # 1 ou -1
        try:
            self.sens = int(sens)
            if self.sens not in (-1, 1):
                self.sens = 1
        except Exception:
            self.sens = 1

        self.decalage = 0
        self.sens_direction = 1
        
        # position courante en pixels
        if self.dir == 1:
            self.x = self.origine_x
            self.y = self.origine_y
        else:
            self.x = self.origine_x
            self.y = self.origine_y
        
        # pour transmettre le déplacement auxentités
        self.dernier_dx = 0
        self.dernier_dy = 0
        
        # taille de la plateforme (1 cellule)
        self.largeur = TAILLE_CELLULE
        self.hauteur = TAILLE_CELLULE
        
        # couleur (par defaut noir)
        self.couleur = "noir"

    def maj(self):
        """Met à jour la position et retourne (dx, dy)."""
        old_x = self.x
        old_y = self.y
        # avancer le décalage
        self.decalage += self.vitesse * self.sens_direction
        if self.decalage > self.plage:
            self.decalage = self.plage
            self.sens_direction = -1
        if self.decalage < 0:
            self.decalage = 0
            self.sens_direction = 1
        if self.dir == 1:
            # horizontal
            self.x = int(self.origine_x + self.sens * self.decalage)
            self.y = self.origine_y
        else:
            # vertical
            self.x = self.origine_x
            self.y = int(self.origine_y + self.sens * self.decalage)
        self.dernier_dx = int(self.x - old_x)
        self.dernier_dy = int(self.y - old_y)
        return (self.dernier_dx, self.dernier_dy)

    def obtenir_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur)

    def dessiner(self, ecran):
        draw_color = (30, 30, 30)
        if self.couleur in COULEURS:
            draw_color = COULEURS[self.couleur]
        elif self.couleur == 'noir':
            draw_color = (30, 30, 30)
        pygame.draw.rect(ecran, draw_color, (int(self.x), int(self.y), self.largeur, self.hauteur))


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self):
        self.grille = []
        self.spawn_cell = None
        self.numero_niveau = 1
        self.gestionnaire_config = ConfigManager()
        # entités du niveau
        self.sorciers = []
        self.squelettes = []
        self.projectiles = []
        self.slimes = []
        self.pieces = []
        # plateformes mobiles
        self.platformes_mobiles = []
        self.traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic"]
        self.image_pic = pygame.image.load("img/pic.png")
        self.image_pic = pygame.transform.scale(self.image_pic, (TAILLE_CELLULE, TAILLE_CELLULE))
        self.image_porte = pygame.image.load("img/porte.png")
        self.image_porte = pygame.transform.scale(self.image_porte, (TAILLE_CELLULE, TAILLE_CELLULE))

        # Sons aléatoires pour le sorcier (tir) et le squelette (attaque)
        self.sons_sorcier_shot = []
        for i in range(1, 4):
            son = pygame.mixer.Sound(os.path.join("audio", "sorcier_shot" + str(i) + ".mp3"))
            self.sons_sorcier_shot.append(son)
        self.sons_squelette_tape = []
        for i in range(1, 4):
            son = pygame.mixer.Sound(os.path.join("audio", "squelette_tape" + str(i) + ".wav"))
            self.sons_squelette_tape.append(son)
        self.maj_volume_sons()

        # stocker les infos des étoiles pour le fond
        self.etoiles_fond = []
        for _ in range(100):
            x = random.randint(0, LARGEUR_ECRAN)
            y = random.randint(0, int(HAUTEUR_ECRAN * 0.7))
            taille = random.randint(1, 2)
            brillance = random.randint(100, 255)
            vitesse_scintillement = random.uniform(0.02, 0.08)
            phase = random.uniform(0, 2 * math.pi)
            self.etoiles_fond.append([x, y, taille, brillance, vitesse_scintillement, phase])
        self.dernier_tick_maj_plat = -1
    
    def maj_volume_sons(self):
        """Met à jour le volume des sons d'ennemis"""
        volumes = self.gestionnaire_config.obtenir_volumes()
        vol_effets = volumes.get("effets", 50) / 100
        for son in self.sons_sorcier_shot:
            son.set_volume(vol_effets)
        for son in self.sons_squelette_tape:
            son.set_volume(vol_effets)

    def creer_grille_vide(self):
        """Crée une grille vide"""
        self.grille = []
        for b in range(HAUTEUR_GRILLE):
            ligne = []
            for a in range(LARGEUR_GRILLE):
                ligne.append("vide")
            self.grille.append(ligne)
    
    def charger_depuis_json(self, numero):
        """Charge un niveau depuis un fichier JSON"""
        self.numero_niveau = numero
        chemin = "niveaux/niveau_" + str(numero) + ".json"
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.creer_grille_vide()
        self.spawn_cell = None
        # reset
        self.sorciers = []
        self.projectiles = []
        self.squelettes = []
        self.slimes = []
        self.pieces = []
        self.platformes_mobiles = []
        for type_bloc, positions in data.items():
            if type_bloc == "spawn":
                x, y = positions
                self.spawn_cell = (x, y)
                self.grille[y][x] = "vide"
            elif type_bloc == "sorcier":
                for item in positions:
                    # valeurs par défaut
                    dirv = 1
                    range_blocks = None

                    if type(item) == list or type(item) == tuple:
                        # cas où la direction et/ou range sont fournis
                        if len(item) >= 3:
                            x = item[0]
                            y = item[1]
                            dirv = int(item[2])
                            if len(item) >= 4:
                                range_blocks = int(item[3])
                        else:
                            x = item[0]
                            y = item[1]
                    else:
                        # tenter de déballer d'autres types (sécurité)
                        try:
                            x = item[0]
                            y = item[1]
                        except Exception:
                            continue

                    # créer sorcier à la position (pixels)
                    px = x * TAILLE_CELLULE
                    if dirv == 1:
                        direction_val = 1
                    else:
                        direction_val = -1
                    sorcier = Sorcier(px, 0, direction=direction_val, shoot_range_blocks=range_blocks)

                    rect_w = sorcier.width - 2 * sorcier.marge_x
                    cell_cx = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    new_rect_left = cell_cx - rect_w // 2
                    sorcier.x = int(new_rect_left - sorcier.marge_x)

                    cell_top_px = y * TAILLE_CELLULE
                    rect_h = sorcier.height - sorcier.marge_y_haut - sorcier.marge_y_bas
                    rect_top = cell_top_px - rect_h
                    sorcier.y = int(rect_top - sorcier.marge_y_haut + 53)

                    # mettre à jour la rect en fonction de la nouvelle position
                    sorcier.rect.topleft = (int(sorcier.x + sorcier.marge_x), int(sorcier.y + sorcier.marge_y_haut))

                    self.sorciers.append(sorcier)
                    # laisser la case vide pour ne pas bloquer le joueur
                    self.grille[y][x] = "vide"
            elif type_bloc == "squelette":
                for item in positions:
                    if type(item) == list or type(item) == tuple:
                        if len(item) >= 3:
                            x = item[0]
                            y = item[1]
                            dirv = int(item[2])
                            if len(item) >= 4:
                                walk_blocks = int(item[3])
                            else:
                                walk_blocks = 3
                        else:
                            x = item[0]
                            y = item[1]
                            dirv = 1
                            walk_blocks = 3

                    # créer squelette à la position
                    px = x * TAILLE_CELLULE
                    if dirv == 1:
                        direction_val = 1
                    else:
                        direction_val = -1
                    squelette = Squelette(px, 0, direction=direction_val, walk_blocks=walk_blocks)

                    rect_w = squelette.width - 2 * squelette.marge_x
                    cell_cx = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                    new_rect_left = cell_cx - rect_w // 2
                    squelette.x = int(new_rect_left - squelette.marge_x)

                    cell_top_px = y * TAILLE_CELLULE
                    rect_h = squelette.height - squelette.marge_y_haut - squelette.marge_y_bas
                    rect_top = cell_top_px - rect_h
                    squelette.y = int(rect_top - squelette.marge_y_haut + 50)

                    # mettre à jour la rect en fonction de la nouvelle position
                    squelette.rect.topleft = (int(squelette.x + squelette.marge_x), int(squelette.y + squelette.marge_y_haut))

                    squelette.origin_x = squelette.x

                    self.squelettes.append(squelette)
                    self.grille[y][x] = "vide"
            elif type_bloc == "slime_vert" or type_bloc == "slime_violet":
                if type_bloc == "slime_vert":
                    couleur_slime = "vert"
                else:
                    couleur_slime = "violet"
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    px = x * TAILLE_CELLULE
                    py = y * TAILLE_CELLULE
                    slime = Slime(px, py, couleur=couleur_slime)
                    self.slimes.append(slime)
                    self.grille[y][x] = "vide"
            elif type_bloc == "piece":
                pieces_deja = self.gestionnaire_config.obtenir_pieces_collectees(numero)
                for pos in positions:
                    x = pos[0]
                    y = pos[1]
                    # Vérifier si cette pièce a déjà été collectée
                    deja_collectee = False
                    for p in pieces_deja:
                        if p[0] == x and p[1] == y:
                            deja_collectee = True
                            break
                    if deja_collectee:
                        self.grille[y][x] = "vide"
                        continue
                    px = x * TAILLE_CELLULE
                    py = y * TAILLE_CELLULE
                    piece = Piece(px, py)
                    piece.cell_x = x
                    piece.cell_y = y
                    self.pieces.append(piece)
                    self.grille[y][x] = "vide"
            elif type_bloc.startswith("mobile_"):
                parts = type_bloc.split("_")
                if len(parts) >= 2:
                    couleur = parts[1]
                else:
                    continue
                # positions: [x, y, dir, range, sens, speed]
                for item in positions:
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except Exception:
                        continue

                    dirv = 1
                    sens = 1
                    range_blocks = 1
                    speed_px = 1.0

                    try:
                        if len(item) >= 3:
                            dirv = int(item[2])

                        if len(item) >= 6:
                            a3 = int(item[3])
                            a4 = int(item[4])
                            # détecter le sens (-1 ou 1)
                            if a3 in (-1, 1) and a4 not in (-1, 1):
                                sens = a3
                                range_blocks = int(item[4])
                            elif a4 in (-1, 1) and a3 not in (-1, 1):
                                range_blocks = int(item[3])
                                sens = a4
                            else:
                                if a3 in (-1, 1):
                                    sens = a3
                                else:
                                    sens = 1
                                range_blocks = int(item[4])
                            speed_px = float(item[5])
                        elif len(item) == 5:
                            a3 = int(item[3])
                            a4 = int(item[4])
                            if a3 in (-1, 1) and a4 not in (-1, 1):
                                sens = a3
                                range_blocks = a4
                            elif a4 in (-1, 1) and a3 not in (-1, 1):
                                range_blocks = a3
                                sens = a4
                            else:
                                range_blocks = a3
                                if a4 in (-1, 1):
                                    sens = a4
                                else:
                                    sens = 1
                        elif len(item) == 4:
                            range_blocks = int(item[3])
                            sens = 1
                        elif len(item) == 3:
                            dirv = int(item[2])
                            sens = 1
                            range_blocks = 1
                    except Exception:
                        continue

                    plat = PlateformeMobile(x, y, dirv=dirv, range_blocks=range_blocks, sens=sens, speed_px=speed_px)
                    plat.couleur = couleur
                    self.platformes_mobiles.append(plat)
                    # ne pas laisser de bloc dans la grille (plateforme gérée séparément)
                    self.grille[y][x] = "vide"
            else:
                for pos in positions:
                    x, y = pos
                    self.grille[y][x] = type_bloc
        
        return self.grille

    def obtenir_spawn_pixel(self):
        """Retourne la position de spawn en pixels (x_px, y_px) ou None si absent."""
        if self.spawn_cell is None:
            return None
        x_cell, y_cell = self.spawn_cell
        x_px = x_cell * TAILLE_CELLULE
        y_px = y_cell * TAILLE_CELLULE - TAILLE_CELLULE # pour que le joueur soit au-dessus du sol
        return (x_px, y_px)
    
    def charger_niveau(self, numero, ecran):
        """Charge le niveau correspondant au numéro"""
        self.grille = self.charger_depuis_json(numero)

    def reset(self, numero, ecran):
        """Réinitialise le niveau"""
        self.charger_niveau(numero, ecran)
    
    def obtenir_bloc(self, x, y):
        """Retourne le type de bloc à une position donnée"""
        if 0 <= x < LARGEUR_GRILLE and 0 <= y < HAUTEUR_GRILLE:
            return self.grille[y][x]
        return "vide"
    
    def collision(self, rect, couleur_joueur):
        """Vérifie si un rectangle entre en collision avec un bloc solide"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                # Blocs toujours solides
                if bloc == "noir":
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
                
                # Blocs de couleur (solides seulement si même couleur)
                elif bloc in ["rouge", "bleu", "vert", "gris"] and bloc == couleur_joueur:
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if rect.colliderect(bloc_rect):
                        return True
        # plateformes
        for plat in self.platformes_mobiles:
            pr = plat.obtenir_rect()
            if plat.couleur is None or plat.couleur == "noir":
                if rect.colliderect(pr):
                    return True
            else:
                if plat.couleur in ["rouge", "bleu", "vert", "gris"] and plat.couleur == couleur_joueur:
                    if rect.colliderect(pr):
                        return True
        return False

    def bloc_solide_au_dessus(self, joueur):
        """Vérifie s'il y a un bloc solide juste au-dessus du joueur"""
        # Zone de détection au-dessus de la tête du joueur
        head_y = joueur.y + joueur.marge_y_haut
        detection_height = 10
        
        detection_rect = pygame.Rect(
            joueur.x + joueur.marge_x + 5,
            head_y - detection_height,
            joueur.largeur - 2 * joueur.marge_x - 10,
            detection_height
        )
        
        # blocs solides
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                if bloc == "noir" or (bloc in ["rouge", "bleu", "vert", "gris"] and bloc == joueur.couleur):
                    bloc_rect = pygame.Rect(x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE)
                    if detection_rect.colliderect(bloc_rect):
                        return True
        
        # collision avec plateformes mobiles
        for plat in self.platformes_mobiles:
            # Ignorer si les plateformes de couleur différente
            if plat.couleur is not None and plat.couleur != "noir" and plat.couleur != joueur.couleur:
                continue
            pr = plat.obtenir_rect()
            if detection_rect.colliderect(pr):
                return True
        
        return False
    
    def dessiner(self, ecran, temps_global=0, update_entities=True):
        """Dessine tous les blocs du niveau"""
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                bloc = self.grille[y][x]
                
                if bloc != "vide":
                    if bloc == "pic" and self.image_pic:
                        ecran.blit(self.image_pic, (x * TAILLE_CELLULE, y * TAILLE_CELLULE))
                    
                    elif bloc == "porte" and self.image_porte:
                        # Dessiner l'image du portail d'arrivée sur 2 blocs de hauteur
                        image_porte_haute = pygame.transform.scale(self.image_porte, (TAILLE_CELLULE, TAILLE_CELLULE * 1.4))
                        ecran.blit(image_porte_haute, (x * TAILLE_CELLULE, y * TAILLE_CELLULE - TAILLE_CELLULE * 0.4))
                    
                    elif "change_" in bloc:
                        # Portails = 3 cercles 
                        couleur = COULEURS[bloc]
                        centre_x = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                        centre_y = y * TAILLE_CELLULE + TAILLE_CELLULE // 2
                        rayon = TAILLE_CELLULE // 2 - 2
                        
                        # Couleur claire pour le cercle intérieur
                        r = min(couleur[0] + 100, 255)
                        g = min(couleur[1] + 100, 255)
                        b = min(couleur[2] + 100, 255)
                        couleur_claire = (r, g, b)
                        
                        # Cercle exterieur (transparent)
                        surface_portail = pygame.Surface((TAILLE_CELLULE, TAILLE_CELLULE), pygame.SRCALPHA)
                        pygame.draw.circle(surface_portail, (couleur[0], couleur[1], couleur[2], 80), (TAILLE_CELLULE // 2, TAILLE_CELLULE // 2), rayon)
                        ecran.blit(surface_portail, (x * TAILLE_CELLULE, y * TAILLE_CELLULE))
                        
                        # Cercle moyen
                        pygame.draw.circle(ecran, couleur, (centre_x, centre_y), rayon - 8)
                        
                        # Cercle intérieur
                        pygame.draw.circle(ecran, couleur_claire, (centre_x, centre_y), rayon - 16)
                    
                    else:
                        # Blocs normaux
                        couleur = COULEURS[bloc]
                        pygame.draw.rect(ecran, couleur, (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
        
        if update_entities:
            # mise à jour plateformes
            self.maj_plateformes(temps_global)
            for plat in list(self.platformes_mobiles):
                plat.dessiner(ecran)
            
            for sorcier in list(self.sorciers):
                proj = sorcier.update()
                if proj is not None:
                    self.projectiles.append(proj)
                    random.choice(self.sons_sorcier_shot).play()
                sorcier.dessiner(ecran)

            for squelette in list(self.squelettes):
                ancien_etat = squelette.state
                squelette.update()
                # Jouer un son quand le squelette commence à attaquer
                if squelette.state == "attacking" and ancien_etat == "pre_attack":
                    random.choice(self.sons_squelette_tape).play()
                squelette.dessiner(ecran)

            proj_list = list(self.projectiles)
            for proj in proj_list:
                proj.update()
                proj_alive = proj.alive
                if not proj_alive:
                    self.projectiles.remove(proj)
                else:
                    proj.dessiner(ecran)

            for slime in list(self.slimes):
                slime.update()
                if not slime.alive:
                    self.slimes.remove(slime)
                else:
                    slime.dessiner(ecran)

            for piece in list(self.pieces):
                piece.update()
                if not piece.alive:
                    self.pieces.remove(piece)
                else:
                    piece.dessiner(ecran)
        else:
            for plat in self.platformes_mobiles:
                plat.dessiner(ecran)
            for sorcier in self.sorciers:
                sorcier.dessiner(ecran)
            for squelette in self.squelettes:
                squelette.dessiner(ecran)
            for proj in self.projectiles:
                proj.dessiner(ecran)
            for slime in self.slimes:
                slime.dessiner(ecran)
            for piece in self.pieces:
                piece.dessiner(ecran)
    def dessiner_fond(self, ecran, couleur_planete, temps_global=0):
        """Dessine le fond pour le niveau basé sur la couleur de la planète.
        """
        # dégradé du ciel
        for y in range(HAUTEUR_ECRAN):
            ratio = y / HAUTEUR_ECRAN
            r = int(10 + ratio * couleur_planete[0] * 0.3)
            g = int(10 + ratio * couleur_planete[1] * 0.3)
            b = int(30 + ratio * couleur_planete[2] * 0.3)
            pygame.draw.line(ecran, (r, g, b), (0, y), (LARGEUR_ECRAN, y))

        # dessiner les étoiles scintillantes
        for etoile in self.etoiles_fond:
            x, y, taille, brillance_base, vitesse, phase = etoile
            brillance = int(brillance_base * 0.5 * (0.5 + 0.5 * math.sin(temps_global * vitesse + phase)))
            brillance = max(30, min(180, brillance))
            pygame.draw.circle(ecran, (brillance, brillance, brillance), (int(x), int(y)), taille)
    
    def dessiner_portail(self, ecran, x, y, taille, temps_global):
        """Dessine un portail de téléportation jaune"""
        
        # Effet de rotation et pulsation
        pulse = 1 + 0.2 * math.sin(temps_global * 0.03)
        rayon = int(taille * pulse)
        
        # Cercles pour l'effet de portail
        for i in range(5):
            alpha = 180 - i * 35
            r = rayon - i * (rayon // 6)
            if r > 0:
                teinte = 200 + int(55 * math.sin(temps_global * 0.02 + i))
                surface = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, teinte, 50, alpha), (r + 5, r + 5), r)
                ecran.blit(surface, (x - r - 5, y - r - 5))
        
        # Particules tourbillonnantes
        for i in range(8):
            angle = temps_global * 0.015 + i * (math.pi / 4)
            dist = rayon * 0.7
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            particle_size = 3 + int(2 * math.sin(temps_global * 0.04 + i))
            pygame.draw.circle(ecran, (255, 255, 150), (px, py), particle_size)
        
        pygame.draw.circle(ecran, (255, 255, 200), (x, y), rayon // 4)

    def maj_plateformes(self, tick):
        """Met à jour toutes les plateformes mobiles."""
        if tick == self.dernier_tick_maj_plat:
            return
        self.dernier_tick_maj_plat = tick
        for plat in self.platformes_mobiles:
            plat.maj()

    def appliquer_pousse_plateforme(self, joueur):
        """collision"""
        rect_joueur = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
        dx_deja_applique = set()

        for plat in self.platformes_mobiles:
            # gestion des interactions de  couleurs
            if plat.couleur is not None and plat.couleur != "noir" and plat.couleur != joueur.couleur:
                continue

            rect_plat = plat.obtenir_rect()
            dx = plat.dernier_dx
            dy = plat.dernier_dy

            # écrasement
            if dy > 0 and rect_joueur.colliderect(rect_plat):
                tete_top = joueur.y + joueur.marge_y_haut
                if tete_top <= rect_plat.bottom - 5:
                    if self.bloc_solide_au_dessus(joueur):
                        return "mort"

                    ancien_plateforme = rect_plat.copy()
                    ancien_plateforme.move_ip(-dx, -dy)
                    if not ancien_plateforme.colliderect(rect_joueur):
                        player_vy = joueur.vitesse_y
                        if player_vy < 0:
                            magnitude_montante = -player_vy
                        else:
                            magnitude_montante = 0
                        if magnitude_montante > abs(dy) + 1:
                            joueur.y = rect_plat.bottom - joueur.marge_y_haut
                            joueur.vitesse_y = 0

            # collision
            if rect_joueur.colliderect(rect_plat):
                cle = (dx, dy)
                if cle not in dx_deja_applique:
                    old_x = joueur.x
                    old_y = joueur.y
                    joueur.x += dx
                    if dy != 0:
                        joueur.y += dy

                    rect_test = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)

                    if self.collision(rect_test, joueur.couleur):
                        joueur.x = old_x
                        rect_test_x = pygame.Rect(joueur.x + joueur.marge_x, old_y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
                        if not self.collision(rect_test_x, joueur.couleur):
                            joueur.y = old_y + dy
                        else:
                            joueur.x = old_x
                            joueur.y = old_y

                    rect_joueur.topleft = (joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut)
                    if dx != 0 or dy != 0:
                        joueur.pousse_plateforme = True
                    dx_deja_applique.add(cle)
                continue

            # debout
            pieds_bottom = joueur.y + joueur.hauteur - joueur.marge_y_bas
            tolerance = 6
            chevauchement_horizontal = not (rect_joueur.right <= rect_plat.left or rect_joueur.left >= rect_plat.right)
            if chevauchement_horizontal and (rect_plat.top - tolerance <= pieds_bottom <= rect_plat.top + 2):
                cle = (dx, dy)
                if cle not in dx_deja_applique:
                    old_x = joueur.x
                    joueur.x += dx
                    rect_test = pygame.Rect(joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut, joueur.largeur - 2 * joueur.marge_x, joueur.hauteur - joueur.marge_y_haut - joueur.marge_y_bas)
                    if self.collision(rect_test, joueur.couleur):
                        joueur.x = old_x
                    else:
                        joueur.pousse_plateforme = True
                    dx_deja_applique.add(cle)

                if joueur.vitesse_y >= 0:
                    joueur.au_sol = True

                rect_joueur.topleft = (joueur.x + joueur.marge_x, joueur.y + joueur.marge_y_haut)
