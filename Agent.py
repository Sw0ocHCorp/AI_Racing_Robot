import pygame
from PIL import Image
import numpy as np
import math

DROITE= 0
GAUCHE= 1
AVANT= 2

class Agent(pygame.sprite.Sprite):
    def __init__(self, velocity, rotation_angle, skin= "Software_Game_Assets\Player_car_final.png", position= (0,0)):
        super().__init__()
        self.SKIN= pygame.image.load(skin)
        self.image= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.img= Image.open(skin)
        self.width, self.height= self.img.size
        self.angle= 0
        self.position= position
        self.rect= self.image.get_rect()   
        self.rect.center= self.position
        #self.hitbox= self.rotate_agent_img(self.angle)
        self.strategy= np.random.randint(3, size= 100)
        #self.strategy= np.ones(100, dtype= int)
        hitbox_color = (255, 0, 0)
        self.SURFACE= pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.hitbox_surface = self.SURFACE
        self.hitbox_surface.fill(hitbox_color)
        self.hitbox_surface.set_alpha(50)
        self.surf = self.hitbox_surface.get_rect()
        self.surf.center= self.rect.center

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
        self.image= pygame.transform.rotate(self.SKIN, angle)
        self.rect= self.image.get_rect(center= self.position)
        self.hitbox_surface = pygame.transform.rotate(self.SURFACE, angle)
        self.surf = self.hitbox_surface.get_rect(center= self.rect.center)
    
        
    def movement(self, isForward= True):
        radian_angle= math.radians(self.angle)
        position= list(self.position)
        #if isForward:
        position[0] -= self.velocity * math.sin(radian_angle)
        self.rect.centerx -= self.velocity * math.sin(radian_angle)
        position[1] -= self.velocity * math.cos(radian_angle)
        self.rect.centery -= self.velocity * math.cos(radian_angle)
        """else:
            position[0] += self.velocity * math.sin(radian_angle)
            self.hitbox.x += self.velocity * math.sin(radian_angle)
            position[1] += self.velocity * math.cos(radian_angle)
            self.hitbox.y += self.velocity * math.cos(radian_angle)"""
        self.position= tuple(position)
        self.surf.x, self.surf.y= self.rect.x, self.rect.y

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
        return action
        
        
    
