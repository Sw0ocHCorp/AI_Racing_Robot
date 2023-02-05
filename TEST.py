def bresenham_v2(x1, y1, x2, y2):
    # Détermination de la direction de la ligne
    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # S'assurer que la ligne se dessine de gauche à droite
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # Initialisation
    dx = x2 - x1
    dy = abs(y2 - y1)
    error = dx / 2
    ystep = -1 if y1 > y2 else 1
    y = y1

    # Boucle principale
    for x in range(x1, x2 + 1):
        if steep:
            print(y, x)  # Affiche les coordonnées des pixels
        else:
            print(x, y)
        error -= dy
        if error < 0:
            y += ystep
            error += dx

bresenham_v2(0, 0, 5, 3)
bresenham_v2(5, 3, 0, 0)
bresenham_v2(5, 0, 0, 3)
bresenham_v2(0, 3, 5, 0)