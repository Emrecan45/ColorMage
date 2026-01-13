import pygame
import json
import random
import math
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS, LARGEUR_ECRAN, HAUTEUR_ECRAN


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self):
        self.grille = []
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
        for type_bloc, positions in data.items():
            for pos in positions:
                x, y = pos
                self.grille[y][x] = type_bloc
        
        return self.grille
    
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
    
    def dessiner(self, ecran, temps_global=0):
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
