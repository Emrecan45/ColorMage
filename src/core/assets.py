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


def charger_son_accelere(chemin, facteur=2.0):
    """Charge un son et renvoie une version jouée plus vite (facteur > 1) ou plus lentement (facteur < 1)."""
    base = pygame.mixer.Sound(chemin)
    try:
        import numpy as np
        arr = pygame.sndarray.array(base)
        idx = np.floor(np.arange(0, len(arr), facteur)).astype(int)
        return pygame.sndarray.make_sound(np.ascontiguousarray(arr[idx]))
    except Exception:
        return base
