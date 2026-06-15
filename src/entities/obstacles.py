import pygame
import core.temps as temps

class FeuBloc:
    def __init__(self, x, y, taille_cellule):
        self.x = x * taille_cellule
        self.y = y * taille_cellule - taille_cellule
        self.visual_x = None
        self.visual_y = None
        self.largeur = taille_cellule
        self.hauteur = taille_cellule * 2
        self.rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        self.alive = True

    def dessiner(self, ecran, frames_feu, frames_fumee, temps_global, taille_cellule):
        if len(frames_feu) == 0:
            return
            
        t = temps.obtenir_temps()
        index_feu = int(t / 90) + int(self.x / taille_cellule) * 2 + int(self.y / taille_cellule)
        index_feu = int(index_feu % len(frames_feu))
        ecran.blit(frames_feu[index_feu], (int(self.x), int(self.y)))
        
        if len(frames_fumee) > 0:
            index_fumee = int(t / 120) + int(self.x / taille_cellule) + int(self.y / taille_cellule)
            index_fumee = int(index_fumee % len(frames_fumee))
            image_fumee = frames_fumee[index_fumee]
            fumee_x = self.x + (taille_cellule - image_fumee.get_width()) / 2
            fumee_y = self.y - int(image_fumee.get_height() * 0.6)
            ecran.blit(image_fumee, (int(fumee_x), int(fumee_y)))

    def obtenir_masque(self, frames_feu, temps_global, taille_cellule):
        if len(frames_feu) == 0:
            return None
        t = temps.obtenir_temps()
        index_feu = int(t / 90) + int(self.x / taille_cellule) * 2 + int(self.y / taille_cellule)
        index_feu = int(index_feu % len(frames_feu))
        return pygame.mask.from_surface(frames_feu[index_feu])

class PicBloc:
    def __init__(self, x, y, taille_cellule):
        self.x = x * taille_cellule
        self.y = y * taille_cellule
        self.visual_x = None
        self.visual_y = None
        self.largeur = taille_cellule
        self.hauteur = taille_cellule
        self.rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        self.alive = True

    def dessiner(self, ecran, image_pic):
        if image_pic is not None:
            ecran.blit(image_pic, (int(self.x), int(self.y)))

    def obtenir_masque(self, image_pic):
        if image_pic is not None:
            return pygame.mask.from_surface(image_pic)
        return None
