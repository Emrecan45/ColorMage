import json
import os
import locale
import hashlib
import hmac

from datetime import datetime

class ConfigManager:
    """Gère la configuration utilisateur (touches, volumes, etc.)"""
    
    def __init__(self, nom_jeu="ColorMage"):
        # Détermine le chemin selon l'OS
        if os.name == 'nt':  # Windows
            chemin_base = os.path.join(os.getenv('APPDATA'), nom_jeu)
        elif os.name == 'posix':  # Linux/macOS
            if os.uname().sysname == 'Darwin':  # macOS
                chemin_base = os.path.join(os.path.expanduser("~"), "Library", "Application Support", nom_jeu)
            else:  # Linux
                chemin_base = os.path.join(os.path.expanduser("~"), ".config", nom_jeu)
        else:
            # Fallback : dossier courant
            chemin_base = os.path.join(os.path.expanduser("~"), ".config", nom_jeu)
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(chemin_base, exist_ok=True)
        
        self.chemin_config = os.path.join(chemin_base, "save.json")
        self.sauvegarde_corrompue = False
        self.config = self.charger_config()
        self.controles = self.config.get("controles", {})
        self.volumes = self.config.get("volumes", {})
        self.niveau_actuel = self.config.get("niveau_actuel", 1)
        self.meilleurs_temps = self.config.get("meilleurs_temps", {})
    
    def ecrire_config_atomique(self, config):
        """Écrit la config de façon a ce que l'écriture d'abord dans un fichier temporaire puis on le renomme = une fermeture du jeu en pleine écriture ne peut pas laisser un save.json corrompu."""
        chemin_tmp = self.chemin_config + ".tmp"
        with open(chemin_tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
        os.replace(chemin_tmp, self.chemin_config)

    def generer_signature(self, config):
        """Génère un HMAC-SHA256 de la config"""
        copie = {}
        for cle in config:
            if cle != "signature":
                copie[cle] = config[cle]
        donnees = json.dumps(copie, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(b"CM_s3cr3t_k3y_2026!", donnees.encode("utf-8"), hashlib.sha256)
        return signature.hexdigest()

    def verifier_signature(self, config):
        """Vérifie que la signature correspond aux données"""
        signature = config.get("signature", None)
        if signature is None:
            return False
        attendue = self.generer_signature(config)
        return hmac.compare_digest(signature, attendue)

    def charger_config(self):
        """Charge la configuration depuis le fichier ou crée un fichier par défaut"""
        # Configuration par défaut
        config_defaut = {
            "controles": {
                "gauche": "left",
                "droite": "right",
                "sauter": "up",
                "tir": "e"
            },
            "volumes": {
                "musique": 50,
                "effets": 50
            },
            "niveau_actuel": 1,
            "meilleurs_temps": {},
            "pseudo": "Mage",
            "pieces_total": 0,
            "pieces_gagnees_total": 0,
            "pieces_collectees": {},
            "powerups_achetes": []
        }
        
        # Si le fichier existe, le charger
        if os.path.isfile(self.chemin_config):
            # Lecture du fichier JSON
            config = None
            try:
                with open(self.chemin_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, ValueError, OSError):
                config = None

            if config is not None and type(config) == dict:
                if "signature" in config:
                    if not self.verifier_signature(config):
                        self.sauvegarde_corrompue = True
                else:
                    self.sauvegarde_corrompue = False

                # Vérifier que toutes les sections existent
                if "controles" not in config:
                    config["controles"] = config_defaut["controles"]
                if "volumes" not in config:
                    config["volumes"] = config_defaut["volumes"]
                
                # Vérifier que toutes les touches nécessaires sont présentes
                for cle in config_defaut["controles"]:
                    if cle not in config["controles"]:
                        config["controles"][cle] = config_defaut["controles"][cle]
                
                # Vérifier que tous les volumes sont présents
                for cle in config_defaut["volumes"]:
                    if cle not in config["volumes"]:
                        config["volumes"][cle] = config_defaut["volumes"][cle]
                config["signature"] = self.generer_signature(config)
                self.ecrire_config_atomique(config)

                return config
            # Fichier corrompu = on repart sur une config par défaut propre
            self.sauvegarde_corrompue = True
        
        # Sinon, créer le fichier avec config par défaut
        # Adapter les touches selon le clavier (AZERTY/QWERTY)
        lang = locale.getdefaultlocale()[0]
        est_azerty = lang and lang.startswith("fr")
        
        if est_azerty:
            # Conversion pour AZERTY
            conversion_azerty = {"gauche": "left", "droite": "right", "sauter": "up", "tir": "e"}
            config_defaut["controles"].update(conversion_azerty)
        
        self.sauvegarder_config(config_defaut)
        return config_defaut
    
    def sauvegarder_config(self, config=None):
        """Sauvegarde la configuration dans le fichier utilisateur"""
        if config is None:
            config = {
                "controles": self.controles,
                "volumes": self.volumes,
                "niveau_actuel": self.niveau_actuel,
                "meilleurs_temps": self.meilleurs_temps,
                "pseudo": self.config.get("pseudo", "Joueur"),
                "avatar_profil": self.config.get("avatar_profil", 0),
                "avatars_achetes": self.config.get("avatars_achetes", [0]),
                "pieces_total": self.config.get("pieces_total", 0),
                "pieces_gagnees_total": self.config.get("pieces_gagnees_total", 0),
                "pieces_collectees": self.config.get("pieces_collectees", {}),
                "pages_vues": self.config.get("pages_vues", []),
                "powerups_achetes": self.config.get("powerups_achetes", [])
            }
        # Ajouter la signature anti triche
        config["signature"] = self.generer_signature(config)
        self.ecrire_config_atomique(config)
        self.config = config
        self.controles = config.get("controles", {})
        self.volumes = config.get("volumes", {})
        self.niveau_actuel = config.get("niveau_actuel", 1)
        self.meilleurs_temps = config.get("meilleurs_temps", {})
        
    def obtenir_controles(self):
        """Retourne les touches actuelles en relisant le fichier"""
        self.controles = self.config.get("controles", {})
        return self.controles
    
    def obtenir_volumes(self):
        """Retourne les volumes actuels en relisant le fichier"""
        self.volumes = self.config.get("volumes", {})
        return self.volumes
    
    def obtenir_chemin_config(self):
        """Retourne le chemin du fichier de configuration"""
        return self.chemin_config

    def obtenir_niveau_actuel(self):
        """Retourne le niveau actuel du joueur"""
        return self.config.get("niveau_actuel", 1)

    def obtenir_meilleur_temps(self, niveau):
        """Retourne le meilleur temps (en ms) sauvegardé pour un niveau

        Args:
            niveau: numéro du niveau (int)

        Returns:
            int ou None: meilleur temps en millisecondes si présent, sinon None
        """
        self.meilleurs_temps = self.config.get("meilleurs_temps", {})
        return self.meilleurs_temps.get(str(niveau), None)
        
    def maj_controle(self, action, touche):
        """Met à jour une touche spécifique et sauvegarde"""
        self.controles[action] = touche
        self.sauvegarder_config()
    
    def maj_volume(self, type_volume, valeur, sauvegarder=True):
        """Met à jour un volume spécifique et sauvegarde
        
        Args:
            type_volume: "musique" ou "effets"
            valeur: valeur entre 0 et 100
        """
        self.volumes[type_volume] = int(valeur)
        if sauvegarder:
            self.sauvegarder_config()

    def maj_niveau_actuel(self, niveau):
        """Met à jour le niveau actuel du joueur"""
        self.niveau_actuel = int(niveau)
        self.sauvegarder_config()
    
    def maj_meilleur_temps(self, niveau, temps_ms):
        """Met à jour le meilleur temps pour un niveau si c'est un record
        
        Args:
            niveau: Numéro du niveau
            temps_ms: Temps réalisé en millisecondes
            
        Returns:
            bool: True si c'est un nouveau record, False sinon
        """
        self.meilleurs_temps = self.config.get("meilleurs_temps", {})
        
        niveau_str = str(niveau)
        ancien_temps = self.meilleurs_temps.get(niveau_str, None)
        
        # Si pas de temps enregistré ou nouveau temps meilleur
        if ancien_temps is None or temps_ms < ancien_temps:
            self.meilleurs_temps[niveau_str] = temps_ms
            self.sauvegarder_config()
            return True
        return False

    def reinitialiser_sauvegarde(self):
        """Réinitialise UNIQUEMENT la progression (pas les contrôles/volumes, sauf pseudo)"""
        # Sauvegarder le pseudo, les contrôles et volumes
        pseudo_actuel = self.config.get("pseudo", "Joueur")
        controles_actuels = self.config.get("controles", {"gauche": "left", "droite": "right", "sauter": "up", "tir": "e"})
        volumes_actuels = self.config.get("volumes", {"musique": 50, "effets": 50})
        
        # Reset la progression
        self.config["niveau_actuel"] = 1
        self.config["meilleurs_temps"] = {}
        self.config["avatar_profil"] = 0  # Reset l'avatar du profil
        self.config["avatars_achetes"] = [0]
        self.config["pieces_total"] = 0
        self.config["pieces_gagnees_total"] = 0
        self.config["pieces_collectees"] = {}
        self.config["pages_vues"] = []
        self.config["powerups_achetes"] = []
        
        # Restaurer les paramètres et le pseudo
        self.config["pseudo"] = pseudo_actuel
        self.config["controles"] = controles_actuels
        self.config["volumes"] = volumes_actuels
        
        self.niveau_actuel = 1
        self.meilleurs_temps = {}
        self.pseudo = pseudo_actuel  # Restaurer aussi dans la variable de classe
        
        # Sauvegarder la nouvelle configuration
        self.sauvegarder_config()
    
    def reinitialiser_parametres(self):
        """Réinitialise uniquement les paramètres (contrôles et volumes)"""
        self.controles = {
            "gauche": "left",
            "droite": "right",
            "sauter": "up",
            "tir": "e"
        }
        self.volumes = {
            "musique": 50,
            "effets": 50
        }
        self.config["controles"] = self.controles
        self.config["volumes"] = self.volumes
        self.sauvegarder_config()
    
    def obtenir_pseudo(self):
        """Retourne le pseudo du joueur"""
        return self.config.get("pseudo", "Joueur")
    
    def sauvegarder_pseudo(self, pseudo):
        """Sauvegarde le pseudo du joueur"""
        self.config["pseudo"] = pseudo
        self.sauvegarder_config()

    def ajouter_pieces_gagnees(self, nombre):
        """Ajoute au total les pièces ramassées en terminant un niveau.
        """
        if nombre <= 0:
            return
        self.config["pieces_total"] = self.config.get("pieces_total", 0) + nombre
        self.config["pieces_gagnees_total"] = self.config.get("pieces_gagnees_total", 0) + nombre
        self.sauvegarder_config()

    def obtenir_pieces_total(self):
        """Retourne le nombre total de pièces collectées"""
        return self.config.get("pieces_total", 0)

    def page_vue(self, niveau):
        """Vérifie si la page (du grimoire) d'un niveau a déjà été vue"""
        pages = self.config.get("pages_vues", [])
        return niveau in pages

    def marquer_page_vue(self, niveau):
        """Marque la page (grimoire) d'un niveau comme vue"""
        pages = self.config.get("pages_vues", [])
        if niveau not in pages:
            pages.append(niveau)
            self.config["pages_vues"] = pages
            self.sauvegarder_config()
