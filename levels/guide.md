# Guide des niveaux

## Référence des clés et formats utilisés dans les fichiers de niveaux

### Bases :
- spawn : [x, y]
- porte : [x, y]

### Blocs :
- noir : [x, y]
- bleu : [x, y]
- vert : [x, y]
- rouge : [x, y]
- mobile_"couleur" : [x, y, direction, portée, sens, vitesse]

### Objets :
- pic : [x, y]
- feu : [x, y]
- piece : [x, y]
- change_"couleur" : [x, y]
- cristal_feu : [x, y]

### Ennemis :
- sorcier : [x, y, direction, portée de tir, "drop"]
- squelette : [x, y, direction, portée de marche, "drop"]
- slime_"couleur" : [x, y, "drop"]
- demon : [x, y, "drop"]

### Boss :
- pyrolord : [x, y] ou [x, y, pv]
- porte_boss : [x, y]  (optionnel, sans ca, la porte apparaît automatiquement à la position du boss à sa mort)
