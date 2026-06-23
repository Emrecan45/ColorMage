import asyncio
import os
import sys

# pygame doit être importé ici pour que pygbag l'embarque dans le build web
import pygame

# Ajoute src/ au path pour les imports internes (core, ui, entities)
RACINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RACINE, "src"))

from src.main import Game


async def main():
    jeu = Game()
    await jeu.run()


if __name__ == "__main__":
    asyncio.run(main())
