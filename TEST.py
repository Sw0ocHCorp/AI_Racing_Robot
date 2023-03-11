import pygame

# Définir les couleurs que nous allons utiliser
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Définir la taille de la fenêtre
WINDOW_SIZE = [800, 600]

# Initialiser Pygame
pygame.init()

# Créer la fenêtre
screen = pygame.display.set_mode(WINDOW_SIZE)

# Définir le titre de la fenêtre
pygame.display.set_caption("MCTS Tree Visualization")

# Définir la police pour le texte
font = pygame.font.Font(None, 30)

class Node:
    def __init__(self, state):
        self.state = state
        self.visits = 0
        self.reward = 0
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def update(self, reward):
        self.visits += 1
        self.reward += reward

def draw_node(node, x, y, color):
    # Dessiner un cercle pour représenter le nœud
    pygame.draw.circle(screen, color, [x, y], 20)

    # Dessiner le nombre de visites à l'intérieur du cercle
    text = font.render(str(node.visits), True, BLACK)
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

def draw_tree(node, x, y):
    # Dessiner le nœud actuel
    draw_node(node, x, y, GREEN)

    # Dessiner les enfants du nœud actuel
    num_children = len(node.children)
    if num_children > 0:
        # Calculer l'espacement horizontal entre les enfants
        x_space = WINDOW_SIZE[0] // (num_children + 1)

        # Dessiner les enfants
        for i in range(num_children):
            child = node.children[i]
            child_x = (i + 1) * x_space
            child_y = y + 50
            draw_node(child, child_x, child_y, RED)
            pygame.draw.line(screen, BLACK, [x, y + 20], [child_x, child_y - 20], 2)

            # Dessiner les sous-arbres pour les enfants
            draw_tree(child, child_x, child_y)
            pygame.display.update()


# Exemple d'utilisation de la fonction draw_tree
root = Node(None)
child1 = Node(None)
child2 = Node(None)
root.add_child(child1)
root.add_child(child2)

draw_tree(root, WINDOW_SIZE[0] // 2, 50)

