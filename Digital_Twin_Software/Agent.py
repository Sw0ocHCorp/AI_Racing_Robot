import pygame
from PIL import Image
import numpy as np
import math
from pygame.sprite import Sprite, Group

DROITE= 0
GAUCHE= 1
AVANT= 2
HEIGHT= 900
WIDTH= 1500
WIDTH_ENV= 800
PLAYER_CAR= pygame.image.load("Digital_Twin_Software\Software_Game_Assets\Player_car_final.png")
player_img= Image.open("Digital_Twin_Software\Software_Game_Assets\Player_car_final.png")
ghost_img= Image.open("Digital_Twin_Software\Software_Game_Assets\car1.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size

class Agent(pygame.sprite.Sprite):
    def __init__(self, velocity, rotation_angle, skin= "Digital_Twin_Software\Software_Game_Assets\Player_car_final.png", position= (0,0)):
        super().__init__()
        #-> Stratégie de l'Agent | Version GA
        self.strategy= np.random.randint(3, size= 100)
        #-> Stratégie de l'Agent | Version MCTS
        #self.strategy= np.array([])
        self.SKIN= pygame.image.load(skin)
        self.image= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.angle= 0
        self.simulated_angle= 0
        self.INIT_POSITION= position
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
    
    def rotate_agent_img(self, angle= 45):
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
            if self.angle> 90 and self.angle< 270:
                self.movement(isForward= False)
            else:
                self.movement(isForward= True)
        elif action == GAUCHE:
            self.rotate(True)
            if self.angle> 90 and self.angle< 270:
                self.movement(isForward= False)
            else:
                self.movement(isForward= True)
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

    def set_state(self, position, angle):
        self.position= position
        self.rect.center= position
        self.surf.x, self.surf.y= self.rect.x, self.rect.y
        self.angle= angle
        self.rotate_agent_img(self.angle)

    def reset_state(self):
        self.angle= 0
        self.image= self.SKIN
        self.rect= self.image.get_rect()   
        self.position= self.INIT_POSITION
        self.rect.center= self.position
        hitbox_color = (255, 0, 0)
        self.SURFACE= pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.hitbox_surface = self.SURFACE
        self.hitbox_surface.fill(hitbox_color)
        self.hitbox_surface.set_alpha(50)
        self.surf = self.hitbox_surface.get_rect()
        self.surf.center= self.rect.center

class ReinforcementAgent(pygame.sprite.Sprite):
    def __init__(self, environment, velocity, rotation_angle, skin= "Digital_Twin_Software\Software_Game_Assets\Player_car_final.png", position= (round((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), 4), round(HEIGHT - (PLAYER_HEIGHT/1.7), 4))):
        super().__init__()
        self.SKIN= pygame.image.load(skin)
        self.GHOST_SKIN= pygame.image.load("Digital_Twin_Software\Software_Game_Assets\car1.png")
        self.ghost_image= self.GHOST_SKIN
        self.image= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.angle= 0
        self.INIT_POSITION= position
        self.rect= self.image.get_rect()
        self.rect.center= self.INIT_POSITION
        self.strategy= np.array([])
        self.simulation_angle= 0
        self.simulation_position= self.INIT_POSITION
        self.env= environment
        self.brain= {}
    
    #Fonction de Mouvement de l'Agent
    def set_state(self, position, angle):
        self.position= position
        self.rect.center= position
        self.angle= angle
        self.image= pygame.transform.rotate(self.SKIN, angle)
        self.rect= self.image.get_rect(center= self.position)
    
    def rotate(self, isLeft):
        if isLeft:
            self.angle+= self.rotation_angle
        else:
            self.angle-= self.rotation_angle
        if self.angle > 360:
            self.angle-= 360
        self.image= pygame.transform.rotate(self.SKIN, self.angle)
        self.rect= self.image.get_rect(center= self.rect.center)
    
    def simulated_rotation(self, isLeft, angle= 0):
        if isLeft:
            angle+= self.rotation_angle
        else:
            angle-= self.rotation_angle
        if angle> 360:
            angle-= 360
        return angle

    def movement(self):
        radian_angle= math.radians(self.angle)
        self.rect.centerx -= self.velocity * math.sin(radian_angle)
        self.rect.centery -= self.velocity * math.cos(radian_angle)
    
    def simulated_movement(self, position, angle):
        radian_angle= math.radians(angle)
        location= list(position)
        location[0] -= round(self.velocity * math.sin(radian_angle), 4)
        location[1] -= round(self.velocity * math.cos(radian_angle), 4)
        location= tuple(location)
        return location
    
    def select_action(self, action):
        if action == DROITE:
            self.rotate(False)
            self.movement()
        elif action == GAUCHE:
            self.rotate(True)
            self.movement()
        elif action == AVANT:
            self.movement()
        np.append(self.strategy, action)
    
    def simulated_take_action(self, position, angle, action):
        update_angle= 0
        update_location= (0,0)
        if action == DROITE:
            update_angle= self.simulated_rotation(False, angle)
            update_location= self.simulated_movement(position, update_angle)
        elif action == GAUCHE:
            update_angle= self.simulated_rotation(True, angle)
            update_location= self.simulated_movement(position, update_angle)
        elif action == AVANT:
            update_location= self.simulated_movement(position, angle)
            update_angle= angle
        np.append(self.strategy, action)
        return update_location , update_angle
    
    def get_state_reward(self, position, angle, life_penalty= 0):
        left_location, left_angle= self.simulated_take_action(position, angle, GAUCHE)
        right_location, right_angle= self.simulated_take_action(position, angle, DROITE)
        forward_location, forward_angle= self.simulated_take_action(position, angle, AVANT)
        rewards= [self.get_environment_feedback(left_location, left_angle)- life_penalty, self.get_environment_feedback(right_location, right_angle) - life_penalty, self.get_environment_feedback(forward_location, forward_angle)- life_penalty]
        return rewards

    def get_environment_feedback(self, location, angle):
        assert self.image != None
        ghost_agent= Sprite()
        ghost_agent.rect= self.image.get_rect(center= location)
        ghost_agent.image= pygame.transform.rotate(self.SKIN, angle)
        ghost_agent.rect= ghost_agent.image.get_rect(center= ghost_agent.rect.center)
        collided_sprites= pygame.sprite.spritecollide(ghost_agent, self.env.STATIC_SPRITES, False)
        
        if self.env.FINISH_LINE in collided_sprites:
            return 1
        elif self.env.FINISH_LINE not in collided_sprites and len(collided_sprites) > 0 or (ghost_agent.rect.top > 900 or ghost_agent.rect.bottom > 900):
            """ghost_agent.rect= self.ghost_image.get_rect(center= location)
            ghost_agent.image= pygame.transform.rotate(self.GHOST_SKIN, angle)
            ghost_agent.rect= ghost_agent.image.get_rect(center= ghost_agent.rect.center)
            ghost_group= Group([ghost_agent])
            ghost_group.draw(self.env.w)
            pygame.display.update()
            for event in pygame.event.get():
                pass"""
            return -1
        else:
            return 0

    def reset_state(self):
        self.rect.center= self.INIT_POSITION
        self.strategy= np.array([])
        self.angle= 0
        self.image= self.SKIN
        self.rect= self.image.get_rect(center= self.INIT_POSITION)