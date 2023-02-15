import pygame
from PIL import Image
import numpy as np
import math

DROITE= 0
GAUCHE= 1
AVANT= 2

class Agent:
    def __init__(self, velocity, rotation_angle, skin= "Software_Game_Assets\Player_car_final.png", position= (0,0)):
        self.SKIN= pygame.image.load(skin)
        self.skin= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.img= Image.open(skin)
        self.width, self.height= self.img.size
        self.angle= 0
        self.position= position
        self.hitbox= self.skin.get_rect()   
        self.hitbox.center= self.position
        #self.hitbox= self.rotate_agent_img(self.angle)
        self.strategy= np.random.randint(3, size= 100)
        #self.strategy= np.ones(100, dtype= int)
        hitbox_color = (255, 0, 0)
        self.SURFACE= pygame.Surface(self.hitbox.size, pygame.SRCALPHA)
        self.hitbox_surface = self.SURFACE
        self.hitbox_surface.fill(hitbox_color)
        self.hitbox_surface.set_alpha(50)
        self.surf = self.hitbox_surface.get_rect()
        self.surf.center= self.hitbox.center

    def rotate(self, isLeft):
        angle= 0
        if isLeft:
            self.angle += self.rotation_angle
            angle= 45
        else:
            self.angle -= self.rotation_angle
            angle= -45
        if self.angle > 360:
            self.angle= 0
        self.rotate_agent_img(self.angle)
    
    def rotate_agent_img(self, angle= 45):
        self.skin= pygame.transform.rotate(self.SKIN, angle)
        self.hitbox= self.skin.get_rect(center= self.position)
        self.hitbox_surface = pygame.transform.rotate(self.SURFACE, angle)
        self.surf = self.hitbox_surface.get_rect(center= self.hitbox.center)
    
    def wall_collision(self, first_point, last_point):  #Dans le Tuple on a (Colonne, Ligne)
        line_coords= self.bresenham_algorithm(first_point, last_point)
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
            self.hitbox.x -= self.velocity * math.sin(radian_angle)
            position[1] -= self.velocity * math.cos(radian_angle)
            self.hitbox.y -= self.velocity * math.cos(radian_angle)
        else:
            position[0] += self.velocity * math.sin(radian_angle)
            self.hitbox.x += self.velocity * math.sin(radian_angle)
            position[1] += self.velocity * math.cos(radian_angle)
            self.hitbox.y += self.velocity * math.cos(radian_angle)
        self.position= tuple(position)
        self.surf.x, self.surf.y= self.hitbox.x, self.hitbox.y

    def select_action(self, action):
        if action == DROITE:
            self.rotate(False)
        elif action == GAUCHE:
            self.rotate(True)
        elif action == AVANT:
            if self.angle> 90 and self.angle< 270:
                self.movement(isForward= False)
            else:
                self.movement(isForward= True)
        

    def bresenham_algorithm(self, first_point, last_point):
        coords= np.empty((0,2))
        new_point= []
        fp_tuple= None
        lp_tuple= None
        # Détermination de la direction de la ligne
        steep = last_point[1] - first_point[1] > 0 or last_point[0] - first_point[0] > 0
        isFlip= False
        # S'assurer que la ligne se dessine de gauche à droite
        if first_point[0] > last_point[0]:
            fp_tuple= (last_point[0], last_point[1])
            lp_tuple= (first_point[0], first_point[1])
        # Initialisation
        if fp_tuple is not None and lp_tuple is not None:
            first_point= fp_tuple
            last_point= lp_tuple
        if abs(int(first_point[0]) - int(last_point[0])) >= abs(int(first_point[1]) - int(last_point[1])):
            dx = last_point[0] - first_point[0]
            dy = abs(last_point[1] - first_point[1])
            error = dx / 2
            ystep = -1 if first_point[1] > last_point[1] else 1
            # Boucle principale
            y = first_point[1]
            for x in range(int(first_point[0]), int(last_point[0]) + 1):
                new_point= [np.float32(x),y]
                coords= np.append(coords, [new_point], axis= 0)
                error -= dy
                if error < 0:
                    y += ystep
                    error += dx
        else:
            dx = abs(last_point[0] - first_point[0])
            dy = last_point[1] - first_point[1]
            error = dy / 2
            xstep = -1 if first_point[0] > last_point[0] else 1
            x= first_point[0]
            for y in range(int(first_point[1]), int(last_point[1]) + 1):
                new_point= [x,np.float32(y)]
                coords= np.append(coords, [new_point], axis= 0)
                error -= dx
                if error < 0:
                    x += xstep
                    error += dy
        # Inversion de la ligne si nécessaire
        return coords
        
    
