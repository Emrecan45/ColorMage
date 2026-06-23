import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
RACINE = TOOLS.parent
STAGING = RACINE / "build" / "ColorMage"
TEMPLATE = TOOLS / "web.tmpl"  # template HTML custom (correctif HiDPI)

FICHIERS_RACINE_WEB = [
    RACINE / "assets" / "video" / "video_intro.mp4",
    RACINE / "assets" / "img" / "ui" / "logo.ico",
]

for fichier_audio in sorted((RACINE / "assets" / "audio").glob("*")):
    if fichier_audio.suffix.lower() in (".wav", ".ogg") and not fichier_audio.name.startswith("placeholder_planet"):
        FICHIERS_RACINE_WEB.append(fichier_audio)

# Seuls ces elements sont embarques dans le paquet web
A_COPIER = ["main.py", "src", "assets", "levels"]

# Dossiers et extensions exclus du paquet (inutiles sur le web)
DOSSIERS_EXCLUS = {"__pycache__", "video"}
EXTENSIONS_EXCLUES = (".pyc", ".ico", ".wav", ".ogg")
PREFIXES_EXCLUS = ("placeholder_planet", "screenshot")


def ignorer(dossier, noms):
    """Filtre passe a shutil.copytree pour ne pas copier le superflu."""
    exclus = []
    for nom in noms:
        if nom in DOSSIERS_EXCLUS:
            exclus.append(nom)
        elif nom.lower().endswith(EXTENSIONS_EXCLUES):
            exclus.append(nom)
        elif nom.lower().startswith(PREFIXES_EXCLUS):
            exclus.append(nom)
    return exclus


def stager():
    """Copie le strict necessaire dans un dossier de staging propre."""
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    for nom in A_COPIER:
        source = RACINE / nom
        cible = STAGING / nom
        if source.is_dir():
            shutil.copytree(source, cible, ignore=ignorer)
        elif source.exists():
            shutil.copy2(source, cible)
        else:
            print(f"  ! introuvable, ignore : {nom}")

    print(f"Fichiers prepares dans : {STAGING}")


def builder():
    """Lance pygbag sur le dossier de staging."""
    # Options transmises telles quelles a pygbag (--archive, --build, ...)
    options = sys.argv[1:]

    # --disable-sound-format-error : nos bruitages .wav (PCM) sont lus par SDL_mixer
    args = [sys.executable, "-m", "pygbag", "--disable-sound-format-error", "--template", str(TEMPLATE)]
    for option in options:
        args.append(option)
    args.append(str(STAGING / "main.py"))

    print("Lancement de pygbag...\n")

    sert = "--build" not in options and "--archive" not in options
    if sert:
        # serveur bloquant : on copie l'intro des que le dossier web existe
        import threading
        import time

        def copier_quand_pret():
            web = STAGING / "build" / "web"
            for _ in range(180):
                if (web / "index.html").exists():
                    time.sleep(1)
                    ajouter_fichiers_racine(options)
                    print("\nServeur de test : ouvre http://localhost:8000 dans ton navigateur.")
                    return
                time.sleep(1)

        threading.Thread(target=copier_quand_pret, daemon=True).start()
        subprocess.run(args, check=True)
        return

    subprocess.run(args, check=True)
    ajouter_fichiers_racine(options)

    if "--archive" in options:
        print(f"\nPaquet pret a uploader : {STAGING / 'build' / 'web.zip'}")
    else:
        print(f"\nBuild genere dans : {STAGING / 'build' / 'web'}")


def ajouter_fichiers_racine(options):
    """Place l'intro (video + son) a la racine du site, et dans le zip si --archive."""
    web = STAGING / "build" / "web"
    if web.exists():
        for source in FICHIERS_RACINE_WEB:
            if source.exists():
                shutil.copy2(source, web / source.name)
            else:
                print(f"  ! intro introuvable, ignore : {source.name}")

    archive = STAGING / "build" / "web.zip"
    if "--archive" in options and archive.exists():
        with zipfile.ZipFile(archive, "a", zipfile.ZIP_DEFLATED) as zf:
            for source in FICHIERS_RACINE_WEB:
                if source.exists():
                    zf.write(source, source.name)


if __name__ == "__main__":
    stager()
    builder()
