import pygame

class Chronometre:
    """Gère le chronomètre du jeu"""
    
    def __init__(self):
        self.temps_debut = 0
        self.temps_pause_total = 0
        self.temps_pause_debut = 0
        self.actif = False
        self.en_pause = False
        self.font = pygame.font.SysFont(None, 48)
    
    def demarrer(self):
        """Démarre le chronomètre"""
        self.temps_debut = pygame.time.get_ticks()
        self.temps_pause_total = 0
        self.actif = True
        self.en_pause = False
    
    def arreter(self):
        """Arrête le chronomètre"""
        self.actif = False
        self.en_pause = False
    
    def pause(self):
        """Met le chronomètre en pause"""
        if self.actif and not self.en_pause:
            self.temps_pause_debut = pygame.time.get_ticks()
            self.en_pause = True
    
    def reprendre(self):
        """Reprend le chronomètre après une pause"""
        if self.actif and self.en_pause:
            temps_pause = pygame.time.get_ticks() - self.temps_pause_debut
            self.temps_pause_total += temps_pause
            self.en_pause = False
    
    def obtenir_temps(self):
        """Retourne le temps écoulé en millisecondes"""
        if not self.actif:
            return 0
        
        temps_actuel = pygame.time.get_ticks()
        if self.en_pause:
            temps_actuel = self.temps_pause_debut
        
        return temps_actuel - self.temps_debut - self.temps_pause_total
    
    def formater_temps(self, temps_ms):
        """Converti le temps en format MM:SS:MS"""
        minutes = temps_ms // 60000
        secondes = (temps_ms % 60000) // 1000
        millisecondes = (temps_ms % 1000) // 10
        
        texte = str(minutes) + ":"
        if secondes < 10:
            texte += "0" + str(secondes) + ":"
        else:
            texte += str(secondes) + ":"
        if millisecondes < 10:
            texte += "0" + str(millisecondes)
        else:
            texte += str(millisecondes)
        
        return texte
    
    def dessiner(self, ecran, x=20, y=20):
        """Dessine le chronomètre à l'écran"""
        if self.actif or self.en_pause:
            temps_ecoule = self.obtenir_temps()
            texte_chrono = self.formater_temps(temps_ecoule)
            
            surface_chrono = self.font.render(texte_chrono, True, (255, 255, 255))
            ecran.blit(surface_chrono, (x, y))
