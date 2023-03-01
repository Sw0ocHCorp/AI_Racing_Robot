import arcade
from PIL import Image
import numpy as np
import math

DROITE= 0
GAUCHE= 1
AVANT= 2
FRAME_RATE= 1/10


class Agent():
    def __init__(self, velocity, rotation_angle, skin= "Software_Game_Assets\Player_car_final.png", position= (0,0)):
        self.sprite= arcade.Sprite(skin, 1)
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.angle= 0
        self.sprite.position= position
        self.strategy= np.random.randint(3, size= 100)
        
    def set_strat_index(self, index):
        self.action_index= index

    def rotate(self, isLeft, point):
        if isLeft:
            self.angle += self.rotation_angle
        else:
            self.angle -= self.rotation_angle
        if self.angle > 360:
            self.angle= 0
        self.sprite.angle= self.angle
        self.sprite.position= point
        
    def movement(self, isForward= True):
        radian_angle= math.radians(self.angle)
        self.sprite.center_x += self.velocity * math.sin(radian_angle)
        self.sprite.center_y += self.velocity * math.cos(radian_angle)

    def select_action(self, action):
        if action == DROITE:
            self.rotate(False, self.sprite.position)
        elif action == GAUCHE:
            self.rotate(True, self.sprite.position)
        elif action == AVANT:
            self.movement()
        return action
    
