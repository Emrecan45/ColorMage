## 🏗️ Architecture (Refactorisée)

Le code a été entièrement restructuré en classes pour une meilleure maintenabilité :

### Avantages de la nouvelle architecture :

✅ **Encapsulation** : Chaque classe gère ses propres données  
✅ **Modulaire** : Facile d'ajouter de nouveaux niveaux ou mécaniques  
✅ **Réutilisable** : Les classes peuvent être instanciées plusieurs fois  
✅ **Maintenable** : Code organisé et lisible  
✅ **Extensible** : Prêt pour l'héritage (ex: différents types de blocs)

## 📝 Structure de classe

### `Game`
Gère la boucle principale, les événements et la coordination entre les composants.

### `Joueur`
- Position, couleur, physique
- Déplacement et collisions
- Interactions avec les blocs spéciaux

### `Niveau`
- Grille 2D
- Détection de collisions
- Rendu des blocs

### `Popup`
- Affichage de messages (victoire, défaite)
