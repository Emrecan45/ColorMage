import json
import os
import locale

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
        
        self.chemin_config = os.path.join(chemin_base, "controls.json")
        self.config = self.charger_config()
        self.controles = self.config.get("controles", {})
        self.volumes = self.config.get("volumes", {})
    
    def charger_config(self):
        """Charge la configuration depuis le fichier ou crée un fichier par défaut"""
        # Configuration par défaut
        config_defaut = {
            "controles": {
                "gauche": "left",
                "droite": "right",
                "sauter": "up"
            },
            "volumes": {
                "musique": 50,
                "effets": 50
            }
        }
        
        # Si le fichier existe, le charger
        if os.path.isfile(self.chemin_config):
            with open(self.chemin_config, "r", encoding="utf-8") as f:
                config = json.load(f)
                
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
                
                return config
        
        # Sinon, créer le fichier avec config par défaut
        # Adapter les touches selon le clavier (AZERTY/QWERTY)
        lang = locale.getdefaultlocale()[0]
        est_azerty = lang and lang.startswith("fr")
        
        if est_azerty:
            # Conversion pour AZERTY
            conversion_azerty = {"gauche": "left", "droite": "right", "sauter": "up"}
            config_defaut["controles"].update(conversion_azerty)
        
        self.sauvegarder_config(config_defaut)
        return config_defaut
    
    def sauvegarder_config(self, config=None):
        """Sauvegarde la configuration dans le fichier utilisateur"""
        if config is None:
            config = {
                "controles": self.controles,
                "volumes": self.volumes
            }
        with open(self.chemin_config, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
        self.config = config
        self.controles = config.get("controles", {})
        self.volumes = config.get("volumes", {})
    
    def obtenir_controles(self):
        """Retourne les touches actuelles en relisant le fichier"""
        self.config = self.charger_config()
        self.controles = self.config.get("controles", {})
        return self.controles
    
    def obtenir_volumes(self):
        """Retourne les volumes actuels en relisant le fichier"""
        self.config = self.charger_config()
        self.volumes = self.config.get("volumes", {})
        return self.volumes
        
    def maj_controle(self, action, touche):
        """Met à jour une touche spécifique et sauvegarde"""
        self.controles[action] = touche
        self.sauvegarder_config()
    
    def maj_volume(self, type_volume, valeur):
        """Met à jour un volume spécifique et sauvegarde
        
        Args:
            type_volume: "musique" ou "effets"
            valeur: valeur entre 0 et 100
        """
        self.volumes[type_volume] = int(valeur)
        self.sauvegarder_config()
    
    def obtenir_chemin_config(self):
        """Retourne le chemin du fichier de configuration"""
        return self.chemin_config
