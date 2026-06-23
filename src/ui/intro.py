from core.i18n import t
import pygame
import os
import asyncio
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
from core.config import LARGEUR_ECRAN, HAUTEUR_ECRAN, resource_path, EST_WEB

class Intro:
    """Classe pour gérer l'intro vidéo du jeu"""
    
    def __init__(self, ecran, gestionnaire_config, game=None):
        self.ecran = ecran
        self.gestionnaire_config = gestionnaire_config
        self.game = game
        
        # Afficher écran de chargement
        self.afficher_chargement()
        
        # Chemin de la vidéo et de l'audio
        self.video_path = resource_path(os.path.join("assets", "video", "video_intro.mp4"))
        self.audio_path = resource_path(os.path.join("assets/audio", "intro.wav"))
        
        # État
        self.terminee = False
    
    def afficher_chargement(self):
        """Affiche un écran 'Chargement...'"""
        self.ecran.fill((0, 0, 0))
        font = pygame.font.Font(None, 60)
        texte = font.render(t("intro.chargement"), True, (255, 255, 255))
        texte_rect = texte.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2))
        self.ecran.blit(texte, texte_rect)
        pygame.display.flip()
    
    async def lancer_web(self):
        """Joue l'intro web (balise <video> du template) et masque l'overlay 'Chargement...'."""
        import platform
        try:
            if self.gestionnaire_config.config.get("intro_vue", False):
                platform.window.colormage_hide_intro()
                return "termine"
            volumes = self.gestionnaire_config.obtenir_volumes()
            vol_effets = volumes.get("effets", 50) / 100
            platform.window.colormage_play_intro(vol_effets)
            # Attente de la fin
            attente = 0.0
            while not platform.window.colormage_intro_fini:
                await asyncio.sleep(0.05)
                attente += 0.05
                if attente > 16:
                    break
            # Dessiner la barre de chargement sous l'overlay avant de le retirer
            if self.game is not None:
                self.game.preparer_ecran_chargement()
                self.game.dessiner_ecran_chargement(0.0, pygame.time.get_ticks() / 1000.0)
                pygame.display.flip()
            platform.window.colormage_hide_intro()
            self.gestionnaire_config.config["intro_vue"] = True
            self.gestionnaire_config.sauvegarder_config()
        except Exception as exc:
            print(f"Intro web ignoree : {exc}")
            try:
                platform.window.colormage_hide_intro()
            except Exception:
                pass
        return "termine"

    async def lancer(self):
        # Sur le web l'intro est une balise <video> HTML5 (OpenCV indisponible)
        if EST_WEB:
            return await self.lancer_web()

        # Sans OpenCV on passe l'intro
        if not HAS_CV2:
            return "termine"

        # Vrifier si l'intro est dj passe
        if self.gestionnaire_config.config.get("intro_vue", False):
            return "termine"

        try:
            # Ouvrir la vidéo
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                print("Impossible d'ouvrir la vidéo")
                return "menu"
            
            # Obtenir les fps de la vidéo
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30
            
            frame_delay = 1000.0 / fps  # Délai entre frames en millisecondes
            
            # Jouer l'audio séparément
            volumes = self.gestionnaire_config.obtenir_volumes()
            volume_effets = volumes.get("effets", 50) / 100
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.set_volume(volume_effets)
            pygame.mixer.music.play()
            pygame.display.flip()
            await asyncio.sleep(0)

            # variables pour synchro
            temps_debut = pygame.time.get_ticks()
            frame_count = 0
            horloge = pygame.time.Clock()
            
            while cap.isOpened():
                # Limiter les FPS de la boucle Pygame pour pas trop surcharger
                horloge.tick(60)
                await asyncio.sleep(0)
                
                # Gérer les événements
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        cap.release()
                        return "quitter"
                    # Plein écran
                    if self.game is not None:
                        self.game.gerer_plein_ecran_event(evenement)
                        self.ecran = self.game.ecran
                
                # Calculer combien de frames on devrait avoir affiché
                temps_ecoule = pygame.time.get_ticks() - temps_debut
                frames_attendues = int(temps_ecoule / frame_delay)
                
                # Si on est en retard, sauter des frames
                while frame_count < frames_attendues:
                    ret = cap.grab()
                    if not ret:
                        cap.release()
                        pygame.mixer.music.stop()
                        return "menu"
                    frame_count += 1
                
                # Lire et afficher la frame
                await asyncio.sleep(0)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Convertir BGR vers RGB et redimensionner
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (LARGEUR_ECRAN, HAUTEUR_ECRAN), interpolation=cv2.INTER_NEAREST)
                
                # Convertir en surface pygame
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                
                # Afficher
                self.ecran.blit(frame_surface, (0, 0))
                pygame.display.flip()
            
            # Nettoyage
            cap.release()
            pygame.mixer.music.stop()

        except Exception as e:
            print(f"Erreur lors de la lecture de la vidéo: {e}")
            pygame.time.wait(1000)
        return "menu"
