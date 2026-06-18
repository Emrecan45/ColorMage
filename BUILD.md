# Génération de l'exécutable

Procédure pour packager ColorMage en exécutable avec **PyInstaller**.

## Prérequis

Python 3.8 ou supérieur, puis installer les dépendances (PyInstaller est inclus dans `requirements.txt`) :

```bash
pip install -r requirements.txt
```

## Windows (PowerShell)

Depuis la racine du projet :

```powershell
python -m PyInstaller --noconfirm --onefile --windowed --name ColorMage --icon "assets\img\ui\logo.ico" --paths src --add-data "assets;assets" --add-data "levels;levels" src\main.py
```

## Linux / macOS

```bash
python3 -m PyInstaller --noconfirm --onefile --windowed --name ColorMage --icon "assets/img/ui/logo.ico" --paths src --add-data "assets:assets" --add-data "levels:levels" src/main.py
```

## Détail des options

- `--onefile` : un seul fichier exécutable autonome.
- `--windowed` : pas de console (jeu graphique). À retirer pour voir les erreurs en cas de debug.
- `--name ColorMage` : nom de l'exécutable produit.
- `--icon` : icône de l'exécutable (`assets/img/ui/logo.ico`).
- `--paths src` : permet à PyInstaller de résoudre les imports (`core`, `entities`, `ui`).
- `--add-data` : embarque les ressources. `resource_path()` les retrouve via `sys._MEIPASS` une fois figé.

## Résultat

L'exécutable est généré dans `dist/ColorMage.exe`. Il est autonome : aucune installation de Python n'est nécessaire chez l'utilisateur final.

PyInstaller crée aussi `build/` et `ColorMage.spec` (fichiers temporaires).

## Notes

- L'exécutable pèse une centaine de Mo : la majeure partie vient d'**OpenCV** (`opencv-python`), utilisé  pour la vidéo d'intro.
- Builder sur la plateforme cible : un build Windows produit un `.exe` Windows, un build Linux un binaire Linux, etc. (PyInstaller ne fait pas de cross-compilation).
