# Génération des builds

Deux cibles : un **exécutable bureau** et une **version web**.

# Version web

Le jeu est compilé en WebAssembly avec **pygbag** et tourne directement dans le navigateur.

## Prérequis

```bash
pip install -r requirements.txt
```

## Builder et tester en local

Depuis la racine du projet :

```bash
python tools/build_web.py
```

Le script copie le strict nécessaire dans un dossier propre (`build/ColorMage/`) puis lance pygbag et
sert le jeu sur http://localhost:8000. Ouvrir cette adresse pour tester.

## Générer le fichier zip

```bash
python tools/build_web.py --archive
```

Le `.zip` à uploader est généré dans `build/ColorMage/build/web.zip` (≈ 40 Mo).
Il contient `index.html` à la racine

## Déploiement automatique (GitHub Pages)

À chaque push sur `main`, le workflow [`.github/workflows/deploy-web.yml`](.github/workflows/deploy-web.yml) build le jeu et le publie sur **https://emrecan45.github.io/colormage/**.

L'origine de cette URL ne change jamais : les sauvegardes des joueurs (localStorage) persistent entre les mises à jour.

Pour garder la version persistante sur un site, uploader la page [`tools/templates/index.html`](tools/templates/index.html) : elle embarque la version Pages dans une iframe tout en conservant le lecteur du site.

# Exécutable bureau

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
