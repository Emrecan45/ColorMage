import pygame
import json
from config import LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CELLULE, COULEURS


class Niveau:
    """Représente un niveau du jeu avec sa grille"""
    
    def __init__(self):
        self.grille = []
        self.traversables = ["change_rouge", "change_bleu", "change_vert", "porte", "vide", "pic"]
        self.image_pic = pygame.image.load("img/pic.png")
        self.image_pic = pygame.transform.scale(self.image_pic, (TAILLE_CELLULE, TAILLE_CELLULE))
        self.image_porte = pygame.image.load("img/porte.png")
        self.image_porte = pygame.transform.scale(self.image_porte, (TAILLE_CELLULE, TAILLE_CELLULE))
    
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
