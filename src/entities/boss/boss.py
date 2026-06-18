class Boss:
    """Classe d'un boss dans le jeu."""
    # Invulnérabilité (ms) après chaque coup encaissé
    DEGAT_COOLDOWN_DEFAUT = 1000

    def __init__(self, nom="BOSS", pv=10, enrage_seuil=0.5, enrage_scale=1.2, degat_cooldown=None):
        self.nom = nom
        self.pv_max = int(pv)
        self.pv = int(pv)
        self.alive = True
        self.finished = False
        self.enrage = False
        self.enrage_seuil = enrage_seuil
        self.enrage_scale = enrage_scale
        self.annonce_enrage = False
        self.render_scale = 1.0  # facteur visuel pendant le grossissement
        if degat_cooldown is None:
            degat_cooldown = Boss.DEGAT_COOLDOWN_DEFAUT
        self.degat_cooldown = degat_cooldown
        self.dernier_degat = -100000

    @property
    def en_phase2(self):
        """Vrai quand le boss est enragé."""
        return self.enrage

    def ratio_pv(self):
        if self.pv_max <= 0:
            return 0.0
        return max(0.0, self.pv / self.pv_max)

    def appliquer_degats(self, degats=1):
        """Applique les dégâts et déclenche l'enrage. Retourne True si PV = 0."""
        self.pv = max(0, self.pv - degats)
        if (not self.enrage) and self.pv > 0 and self.ratio_pv() <= self.enrage_seuil:
            self.enrage = True
            self.annonce_enrage = True
            self.on_enrage()
        return self.pv <= 0

    def on_enrage(self):
        """Appelé une fois quand le boss s'enrage."""
        pass

    def grandir(self, facteur):
        """Agrandit le boss. À implémenter par la sous-classe."""
        pass

    def texte_annonce_enrage(self):
        """Texte affiché quand le boss s'enrage."""
        return self.nom + " s'est enragé !"

    def consommer_annonce_enrage(self):
        """Renvoie le texte d'annonce une seule fois, puis None."""
        if self.annonce_enrage:
            self.annonce_enrage = False
            return self.texte_annonce_enrage()
        return None
