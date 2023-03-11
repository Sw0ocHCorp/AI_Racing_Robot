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
        #-> Stratégie de l'Agent | Version GA
        #self.strategy= np.random.randint(3, size= 100)
        #-> Stratégie de l'Agent | Version MCTS
        self.strategy= np.array([])
        self.SKIN= pygame.image.load(skin)
        self.image= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.img= Image.open(skin)
        self.width, self.height= self.img.size
        self.angle= 0
        self.simulated_angle= 0
        self.position= position
        self.rect= self.image.get_rect()   
        self.rect.center= self.position
        hitbox_color = (255, 0, 0)
        self.SURFACE= pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.hitbox_surface = self.SURFACE
        self.hitbox_surface.fill(hitbox_color)
        self.hitbox_surface.set_alpha(50)
        self.surf = self.hitbox_surface.get_rect()
        self.surf.center= self.rect.center

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def rotate(self, isLeft, isSimulated= False):
        angle= self.angle
        if isLeft:
            angle += self.rotation_angle
        else:
            angle -= self.rotation_angle
        if self.angle > 360:
            angle= 0
        
        if isSimulated == False:
            self.angle= angle
            self.rotate_agent_img(self.angle)
        else:
            self.simulated_angle= angle
    
    def rotate_agent_img(self, angle= 45, ):
        self.image= pygame.transform.rotate(self.SKIN, angle)
        self.rect= self.image.get_rect(center= self.position)
        self.hitbox_surface = pygame.transform.rotate(self.SURFACE, angle)
        self.surf = self.hitbox_surface.get_rect(center= self.rect.center)
    
        
    def movement(self, isForward= True, isSimulated= False, simulated_angle= 0):
        radian_angle= math.radians(self.angle)
        if isSimulated:
            radian_angle= math.radians(simulated_angle)
        position= list(self.position)
        #if isForward:
        position[0] -= self.velocity * math.sin(radian_angle)
        position[1] -= self.velocity * math.cos(radian_angle)
        """else:
            position[0] += self.velocity * math.sin(radian_angle)
            self.hitbox.x += self.velocity * math.sin(radian_angle)
            position[1] += self.velocity * math.cos(radian_angle)
            self.hitbox.y += self.velocity * math.cos(radian_angle)"""
        if isSimulated == False:
            self.rect.centerx -= self.velocity * math.sin(radian_angle)
            self.rect.centery -= self.velocity * math.cos(radian_angle)
            self.position= tuple(position)
            self.surf.x, self.surf.y= self.rect.x, self.rect.y
        else:
            return tuple(position)

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
        
    def take_simulated_actions(self):
        self.rotate(isLeft= False, isSimulated= True)
        right_angle= self.simulated_angle
        right_child= self.movement(isSimulated= True, simulated_angle= right_angle)
        forward_angle= right_angle - self.rotation_angle
        if right_angle <= 0:
            forward_angle= right_angle + self.rotation_angle
        forward_child= self.movement(isSimulated= True, simulated_angle= forward_angle)
        left_angle= forward_angle- self.rotation_angle
        if forward_angle <= 0:
            left_angle= forward_angle + self.rotation_angle
        left_child= self.movement(isSimulated= True, simulated_angle= left_angle)
        return {0: {"position":right_child, "agent_angle":right_angle}, 
                1: {"position":left_child, "agent_angle":left_angle}, 
                2: {"position":forward_child, "agent_angle":forward_angle}}

    def set_mcts_state(self, position, angle):
        self.position= position
        self.angle= angle
        self.rotate_agent_img(self.angle)

