import pygame
import json
import random
import math
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS, LARGEUR_ECRAN, HAUTEUR_ECRAN
from enemies import Sorcier
from enemies import Squelette


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self):
        self.grille = []
        self.spawn_cell = None
        # entités du niveau
        self.sorciers = []
        self.squelettes = []
        self.projectiles = []
        self.traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic"]
        self.image_pic = pygame.image.load("img/pic.png")
        self.image_pic = pygame.transform.scale(self.image_pic, (TAILLE_CELLULE, TAILLE_CELLULE))
        self.image_porte = pygame.image.load("img/porte.png")
        self.image_porte = pygame.transform.scale(self.image_porte, (TAILLE_CELLULE, TAILLE_CELLULE))

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
        chemin = "niveaux/niveau_" + str(numero) + ".json"
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.creer_grille_vide()
        self.spawn_cell = None
        # reset
        self.sorciers = []
        self.projectiles = []
        self.squelettes = []
        for type_bloc, positions in data.items():
            if type_bloc == "spawn":
                x, y = positions
                self.spawn_cell = (x, y)
                self.grille[y][x] = "vide"
            elif type_bloc == "sorcier":
                for item in positions:
                    if type(item) == list or type(item) == tuple:
                        # cas où la direction est fournie
                        if len(item) >= 3:
                            x = item[0]
                            y = item[1]
                            dirv = int(item[2])
                            if len(item) >= 4:
                                range_blocks = int(item[3])
                            else:
                                range_blocks = None
                        else:
                            x = item[0]
                            y = item[1]
                            dirv = 1
                            range_blocks = None

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
                        # Portails = cercles colorés
                        couleur = COULEURS[bloc]
                        centre_x = x * TAILLE_CELLULE + TAILLE_CELLULE // 2
                        centre_y = y * TAILLE_CELLULE + TAILLE_CELLULE // 2
                        pygame.draw.circle(ecran, couleur, (centre_x, centre_y), TAILLE_CELLULE // 2 - 4)
                    
                    else:
                        # Blocs normaux
                        couleur = COULEURS[bloc]
                        pygame.draw.rect(ecran, couleur, (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                        pygame.draw.rect(ecran, (0, 0, 0), (x * TAILLE_CELLULE, y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
        if update_entities:
            for sorcier in list(self.sorciers):
                proj = sorcier.update()
                if proj is not None:
                    self.projectiles.append(proj)
                sorcier.dessiner(ecran)

            for squelette in list(self.squelettes):
                squelette.update()
                squelette.dessiner(ecran)

            proj_list = list(self.projectiles)
            for proj in proj_list:
                proj.update()
                proj_alive = proj.alive
                if not proj_alive:
                    self.projectiles.remove(proj)
                else:
                    proj.dessiner(ecran)
        else:
            for sorcier in self.sorciers:
                sorcier.dessiner(ecran)
            for proj in self.projectiles:
                proj.dessiner(ecran)
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
        import math
        
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
