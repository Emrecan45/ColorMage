import pygame

cache_images = {}
cache_polices = {}


def police(taille):
    """Retourne une police systeme en cache (SysFont est lent, surtout sur le web)."""
    if taille not in cache_polices:
        cache_polices[taille] = pygame.font.SysFont(None, taille)
    return cache_polices[taille]


def position_centree(texte_surface, font, cx, cy):
    """Position pour centrer le texte sur (cx, cy).
    """
    descente = font.get_descent()
    x = cx - texte_surface.get_width() // 2
    y = cy - texte_surface.get_height() // 2 - descente // 2
    return (x, y)


def charger_image(chemin, mode="alpha"):
    """Charge une image en la gardant en cache."""
    cle = (chemin, mode)
    if cle not in cache_images:
        image = pygame.image.load(chemin)
        if mode == "alpha":
            image = image.convert_alpha()
        elif mode == "convert":
            image = image.convert()
        cache_images[cle] = image
    return cache_images[cle]


def vider_cache():
    """Vide le cache d'images."""
    cache_images.clear()
