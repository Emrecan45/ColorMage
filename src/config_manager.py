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
        self.controles = self.charger_controles()
    
    def charger_controles(self):
        """Charge les touches depuis le fichier ou crée un fichier par défaut"""
        # Configuration par défaut
        controles_defaut = {
            "gauche": "left",
            "droite": "right",
            "sauter": "up"
        }
        
        # Si le fichier existe, le charger
        if os.path.isfile(self.chemin_config):
            with open(self.chemin_config, "r", encoding="utf-8") as f:
                controles = json.load(f)
                # Vérifier que toutes les touches nécessaires sont présentes
                for cle in controles_defaut:
                    if cle not in controles:
                        controles[cle] = controles_defaut[cle]
                return controles
        
        # Sinon, créer le fichier avec config par défaut
        # Adapter les touches selon le clavier (AZERTY/QWERTY)
        lang = locale.getdefaultlocale()[0]
        est_azerty = lang and lang.startswith("fr")
        
        if est_azerty:
            # Conversion pour AZERTY
            conversion_azerty = {"gauche": "left", "droite": "right", "sauter": "up"}
            controles_defaut.update(conversion_azerty)
        
        self.sauvegarder_controles(controles_defaut)
        return controles_defaut
    
    def sauvegarder_controles(self, controles=None):
        """Sauvegarde les touches dans le fichier utilisateur"""
        if controles is None:
            controles = self.controles
        with open(self.chemin_config, "w", encoding="utf-8") as f:
            json.dump(controles, f, ensure_ascii=False)
        self.controles = controles
    
    def obtenir_controles(self):
        """Retourne les touches actuelles en relisant le fichier"""
        self.controles = self.charger_controles() 
        return self.controles
        
    def mettre_a_jour_controle(self, action, touche):
        """Met à jour une touche spécifique et sauvegarde"""
        self.controles[action] = touche
        self.sauvegarder_controles()
    
    def obtenir_chemin_config(self):
        """Retourne le chemin du fichier de configuration"""
        return self.chemin_config
