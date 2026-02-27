import pygame
import os
import cv2
from config import LARGEUR_ECRAN, HAUTEUR_ECRAN

class Intro:
    """Classe pour gérer l'intro vidéo du jeu"""
    
    def __init__(self, ecran, gestionnaire_config):
        self.ecran = ecran
        self.gestionnaire_config = gestionnaire_config
        
        # Afficher écran de chargement
        self.afficher_chargement()
        
        # Chemin de la vidéo et de l'audio
        self.video_path = os.path.join("img", "video_intro.mp4")
        self.audio_path = os.path.join("audio", "intro.wav")
        
        # État
        self.terminee = False
    
    def afficher_chargement(self):
        """Affiche un écran 'Chargement...'"""
        self.ecran.fill((0, 0, 0))
        font = pygame.font.Font(None, 60)
        texte = font.render("Chargement...", True, (255, 255, 255))
        texte_rect = texte.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2))
        self.ecran.blit(texte, texte_rect)
        pygame.display.flip()
    
    def lancer(self):
        """Lance l'intro vidéo avec opencv"""
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
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play()
            
            temps_debut = pygame.time.get_ticks()
            frame_count = 0
            
            while True:
                # Gérer les événements
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        cap.release()
                        return "quitter"
                
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
                
                # Lire et afficher la frame actuelle
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
