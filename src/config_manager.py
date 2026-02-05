import json
import os
import locale

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
        self.config = self.charger_config()
        self.controles = self.config.get("controles", {})
        self.volumes = self.config.get("volumes", {})
        self.niveau_actuel = self.config.get("niveau_actuel", 1)
        self.meilleurs_temps = self.config.get("meilleurs_temps", {})
    
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
            },
            "niveau_actuel": 1,
            "meilleurs_temps": {},
            "pseudo": "Mage",
            "pieces_total": 0,
            "pieces_collectees": {}
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
                "volumes": self.volumes,
                "niveau_actuel": self.niveau_actuel,
                "meilleurs_temps": self.meilleurs_temps,
                "pseudo": self.config.get("pseudo", "Joueur"),
                "tenue_profil": self.config.get("tenue_profil", 0),
                "pieces_total": self.config.get("pieces_total", 0),
                "pieces_collectees": self.config.get("pieces_collectees", {})
            }
        with open(self.chemin_config, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
        self.config = config
        self.controles = config.get("controles", {})
        self.volumes = config.get("volumes", {})
        self.niveau_actuel = config.get("niveau_actuel", 1)
        self.meilleurs_temps = config.get("meilleurs_temps", {})
        
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
    
    def obtenir_chemin_config(self):
        """Retourne le chemin du fichier de configuration"""
        return self.chemin_config

    def obtenir_niveau_actuel(self):
        """Retourne le niveau actuel du joueur"""
        self.config = self.charger_config()
        return self.config.get("niveau_actuel", 1)

    def obtenir_meilleur_temps(self, niveau):
        """Retourne le meilleur temps (en ms) sauvegardé pour un niveau

        Args:
            niveau: numéro du niveau (int)

        Returns:
            int ou None: meilleur temps en millisecondes si présent, sinon None
        """
        self.config = self.charger_config()
        self.meilleurs_temps = self.config.get("meilleurs_temps", {})
        return self.meilleurs_temps.get(str(niveau), None)
        
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
        self.config = self.charger_config()
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
        controles_actuels = self.config.get("controles", {"gauche": "left", "droite": "right", "sauter": "up"})
        volumes_actuels = self.config.get("volumes", {"musique": 50, "effets": 50})
        
        # Reset la progression
        self.config["niveau_actuel"] = 1
        self.config["meilleurs_temps"] = {}
        self.config["tenue_profil"] = 0  # Reset la tenue du profil
        self.config["pieces_total"] = 0
        self.config["pieces_collectees"] = {}
        
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
            "sauter": "up"
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

    def obtenir_pieces_collectees(self, niveau):
        """Retourne la liste des positions [x,y] de pièces déjà collectées pour un niveau"""
        self.config = self.charger_config()
        toutes = self.config.get("pieces_collectees", {})
        return toutes.get(str(niveau), [])

    def sauvegarder_piece_collectee(self, niveau, cell_x, cell_y):
        """Enregistre qu'une pièce a été collectée et incrémente le total"""
        self.config = self.charger_config()
        toutes = self.config.get("pieces_collectees", {})
        niveau_str = str(niveau)
        if niveau_str not in toutes:
            toutes[niveau_str] = []
        position = [cell_x, cell_y]
        # Éviter les doublons
        deja_present = False
        for p in toutes[niveau_str]:
            if p[0] == cell_x and p[1] == cell_y:
                deja_present = True
                break
        if not deja_present:
            toutes[niveau_str].append(position)
            self.config["pieces_collectees"] = toutes
            self.config["pieces_total"] = self.config.get("pieces_total", 0) + 1
            self.sauvegarder_config()

    def obtenir_pieces_total(self):
        """Retourne le nombre total de pièces collectées"""
        self.config = self.charger_config()
        return self.config.get("pieces_total", 0)
