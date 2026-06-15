import pygame

cache_images = {}


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
