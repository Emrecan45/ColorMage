# ColorMage - Version Exécutable Windows

Ce dépôt contient une version exécutable Windows de **ColorMage**.  
Ce fichier README explique comment lancer, mettre à jour et reconstruire le jeu.

## 📦 Contenu du dépôt

- `build.ps1` : Script PowerShell qui construit l’exécutable.
- `dist/ColorMage.exe` : Fichier exécutable généré après execution du script "build.ps1".
- `img/` : Images utilisées par le jeu.
- `src/` : Code source du jeu.
- `README.md` : Ce fichier d’instructions.

## 🚀 Lancer le jeu

1. **Naviguer dans le dossier du projet :**
   ```powershell
   cd ColorMage
   ```

2. **Installer pyinstaller :**
   ```powershell
   pip install pyinstaller
   ```

3. **Donner la permission d'exécution au script de build**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
   
4. **Lancer le script de build** :
   ```powershell
   .\build.ps1
   ```
   
5. **Lancer le jeu** :
   Une fois le build terminé, aller dans "dist" puis double-cliquer sur **"ColorMage.exe"**.
   ou taper cette commande :
   ```powershell
   .\dist\ColorMage.exe
   ```

## ⚠️ Remarques

Le build doit être refait à chaque modification du code ou des images.

Le dossier dist/ contient uniquement l’exécutable final, prêt à être lancé sur Windows.

Les images doivent rester dans le dossier img/ pour que le jeu fonctionne correctement.

🎯 Objectif


Ce projet vise à permettre une installation simple du jeu sur Windows, sans avoir besoin d’installer Python ou d’autres dépendances. Il suffit de lancer ColorMage.exe.

