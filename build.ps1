# build.ps1 - script pour créer l'exécutable du jeu

# Activer l'environnement virtuel si nécessaire
# .\venv\bin\activate

# Supprime les anciens dossiers build/dist et le fichier .spec
Remove-Item -Recurse -Force build, dist, ColorMage.spec -ErrorAction SilentlyContinue

# Lancer PyInstaller
python -m PyInstaller --onefile --windowed --icon=img/icone.ico --add-data "img;img" src/ColorMage.py
