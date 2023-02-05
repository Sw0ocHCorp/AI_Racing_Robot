import pygame
from PIL import Image
import numpy as np
import math

DROITE= 0
GAUCHE= 1
AVANT= 2

class Agent:
    def __init__(self, velocity, rotation_vel, skin= "Software_Game_Assets\Player_car_final.png", position= (0,0)):
        self.skin= pygame.image.load(skin)
        self.velocity= velocity
        self.rotation_vel= rotation_vel
        img= Image.open(skin)
        self.width, self.height= img.size
        self.angle= 0
        self.position= position
        self.hitbox= self.skin.get_rect(center= self.position)
        self.hitbox.topleft= self.position

    def rotate(self, isLeft):
        if isLeft:
            self.angle += self.rotation_vel
        else:
            self.angle -= self.rotation_vel
        if self.angle > 360:
            self.angle= 0
        return self.rotate_agent_img(self.angle)
    
    def rotate_agent_img(self, angle= 45):
        self.skin= pygame.transform.rotate(self.skin, angle)
        new_hitbox= self.skin.get_rect(center= self.skin.get_rect(topleft= self.position).center)
        self.hitbox= new_hitbox
        return new_hitbox
    
    def wall_collision(self, first_point, last_point):  #Dans le Tuple on a (Colonne, Ligne)
        line_coords= self.bresenham_algorithm(first_point[0], first_point[1], last_point[0], last_point[1])
        x_in_collision = np.logical_and(line_coords[:,0] >= self.hitbox.left, line_coords[:,0] <= self.hitbox.right)
        y_in_collision = np.logical_and(line_coords[:,1] >= self.hitbox.top, line_coords[:,1] <= self.hitbox.bottom)
        result = np.any(np.logical_and(x_in_collision, y_in_collision))
        if result:
            return True
        else:
            return False
        
    def movement(self, isForward= True):
        radian_angle= math.radians(self.angle)
        position= list(self.position)
        if isForward:
            position[0] -= self.velocity * math.sin(radian_angle)
            position[1] -= self.velocity * math.cos(radian_angle)
        else:
            position[0] += self.velocity * math.sin(radian_angle)
            position[1] += self.velocity * math.cos(radian_angle)
        self.position= tuple(position)
        self.hitbox= self.skin.get_rect(center= self.position)
        self.hitbox.topleft= self.position

    def select_action():
        pass
        

    def bresenham_algorithm(self, x1, y1, x2, y2):
        coords= np.empty((0,2))
        # Détermination de la direction de la ligne
        steep = abs(y2 - y1) > abs(x2 - x1)
        isFlip= False
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        # S'assurer que la ligne se dessine de gauche à droite
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        else: 
            isFlip= True
        # Initialisation
        dx = x2 - x1
        dy = abs(y2 - y1)
        error = dx / 2
        ystep = -1 if y1 > y2 else 1
        y = y1
        # Boucle principale
        for x in range(int(x1), int(x2) + 1):
            if steep:
                new_point= [np.float32(x),y]
                coords= np.append(coords, [new_point], axis= 0)
            else:
                new_point= [np.float32(x),y]
                coords= np.append(coords, [new_point], axis= 0)
            error -= dy
            if error < 0:
                y += ystep
                error += dx
        # Inversion de la ligne si nécessaire
        if isFlip:
            coords= np.fliplr(coords)
        return coords
        
    
