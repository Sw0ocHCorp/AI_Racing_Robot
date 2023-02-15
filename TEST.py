import pygame
import math

# Initialisez Pygame
pygame.init()
clock= pygame.time.Clock()

# Définissez la taille de la fenêtre
screen = pygame.display.set_mode((400, 300))

# Créez un objet Rect
rect = pygame.Rect(100, 100, 50, 50)

# Boucle de jeu
running = True
while running:
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Créez une image temporaire pour le Rect
    rect_image = pygame.Surface((rect.width, rect.height))
    rect_image.fill((255, 0, 0))

    # Effectuez la rotation
    rotated_image = pygame.transform.rotate(rect_image, 45)

    # Calculez la position de l'image tournée
    rot_rect = rotated_image.get_rect()
    rot_rect.center = rect.center

    # Effacez la fenêtre
    screen.fill((255, 255, 255))

    # Dessinez l'image tournée sur la surface de jeu
    screen.blit(rotated_image, rot_rect)

    # Actualisez l'affichage
    pygame.display.update()

# Quittez Pygame
pygame.quit()
