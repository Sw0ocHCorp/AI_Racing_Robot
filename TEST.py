import matplotlib.pyplot as plt

# Définir les paramètres
parametre = 0.9
# Définir les couleurs pour les états
if parametre < 0:
    couleur = (1, 0, 0)   # Rouge vif
elif parametre <= 0.5:
    couleur = (1, 51*(parametre*10), 0)
elif parametre < 1:
    couleur = ((255-(10*parametre*10)) / 255, 1, 0)
else:
    couleur = (0, 1, 0)   # Vert vif
# Dessiner le carré avec la couleur définie
plt.fill([0, 1, 1, 0], [0, 0, 1, 1], color=couleur)

# Afficher le carré
plt.axis('equal')
plt.show()
