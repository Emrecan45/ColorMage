import pygame
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Popup:
    """Gère l'affichage des popups de victoire et de défaite"""

    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.largeur_popup = 600
        self.hauteur_popup = 400

    def creer_boutons(self, options):
        """Crée les boutons pour un popup avec les options donnés"""
        position_horizontale_popup = (LARGEUR_ECRAN - self.largeur_popup) // 2
        position_verticale_popup = (HAUTEUR_ECRAN - self.hauteur_popup) // 2
        popup_rect = pygame.Rect(position_horizontale_popup, position_verticale_popup, self.largeur_popup, self.hauteur_popup)

        liste_boutons = []
        position_verticale_bouton = popup_rect.top + 160  # position de départ

        for texte_bouton, action_bouton in options:
            largeur_bouton = 260 
            hauteur_bouton = 60
            bouton_rect = pygame.Rect(0, 0, largeur_bouton, hauteur_bouton)
            bouton_rect.center = (popup_rect.centerx, position_verticale_bouton)  # centrer horizontalement
            liste_boutons.append((bouton_rect, action_bouton))
            position_verticale_bouton += 90  # espace entre boutons

        return liste_boutons

    def niveau_existe(self, numero_niveau):
        """Vérifie si un fichier de niveau existe"""
        chemin = "niveaux/niveau_" + str(numero_niveau) + ".json"
        try:
            with open(chemin, "r") as f:
                pass
            return True
        except:
            return False

    def creer_boutons_victoire(self, niveau_actuel):
        """Crée les boutons pour le popup de victoire"""
        options = []
        
        # Vérifier si le niveau suivant existe
        if self.niveau_existe(niveau_actuel + 1):
            options.append(("Niveau suivant", "suivant"))
        
        options.append(("Recommencer", "rejouer"))
        options.append(("Quitter", "quitter"))
        
        return self.creer_boutons(options)
    
    def creer_boutons_defaite(self):
        """Crée les boutons pour le popup de défaite"""
        return self.creer_boutons([("Recommencer", "rejouer"), ("Quitter", "quitter")])

    def dessiner_popup(self, ecran, titre, options_texte, boutons):
        """Dessine un popup avec un titre et des boutons"""
        popup_rect = pygame.Rect((LARGEUR_ECRAN - self.largeur_popup) // 2, (HAUTEUR_ECRAN - self.hauteur_popup) // 2, self.largeur_popup, self.hauteur_popup)

        # Fond du popup
        pygame.draw.rect(ecran, (255, 255, 255), popup_rect)
        pygame.draw.rect(ecran, (0, 0, 0), popup_rect, 4)

        # Titre
        titre_surface = self.font.render(titre, True, (0, 0, 0))
        titre_x = popup_rect.x + (popup_rect.width - titre_surface.get_width()) // 2
        titre_y = popup_rect.y + 80
        ecran.blit(titre_surface, (titre_x, titre_y))

        # Dessiner les boutons
        for i in range(len(boutons)):
            rect = boutons[i][0]
            texte = options_texte[i][0]

            # Effet de la souris sur les boutons (important)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(ecran, (200, 200, 200), rect)
            else:
                pygame.draw.rect(ecran, (230, 230, 230), rect)

            # Bordure du bouton
            pygame.draw.rect(ecran, (0, 0, 0), rect, 3)

            # Texte du bouton
            texte_surface = self.font.render(texte, True, (0, 0, 0))
            texte_x = rect.x + (rect.width - texte_surface.get_width()) // 2
            texte_y = rect.y + (rect.height - texte_surface.get_height()) // 2
            ecran.blit(texte_surface, (texte_x, texte_y))

    def dessiner_popup_victoire(self, ecran, boutons, niveau_actuel):
        """Dessine le popup de victoire"""
        options = []
        
        # Vérifier si le niveau suivant existe
        if self.niveau_existe(niveau_actuel + 1):
            options.append(("Niveau suivant", "suivant"))
        
        options.append(("Recommencer", "rejouer"))
        options.append(("Quitter", "quitter"))
        
        self.dessiner_popup(ecran, "Bravo ! Niveau terminé", options, boutons)

    def dessiner_popup_defaite(self, ecran, boutons):
        """Dessine le popup de défaite"""
        options = [("Recommencer", "rejouer"), ("Quitter", "quitter")]
        self.dessiner_popup(ecran, "Game Over ! Vous êtes mort", options, boutons)
