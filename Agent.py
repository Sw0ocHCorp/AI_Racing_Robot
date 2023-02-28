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
            #print("Left")
            self.angle += self.rotation_angle
        else:
            #print("Right")
            self.angle -= self.rotation_angle
        if self.angle > 360 or self.angle < -360:
            self.angle= abs(self.angle) - 360
        self.sprite.angle= self.angle
        self.sprite.position= point
        """print("--> Si mouvement")
        print("Modif X= " + str(self.velocity * math.sin(math.radians(-self.angle))) + "Modif Y= " + str(self.velocity * math.cos(math.radians(-self.angle))))
        print("--------------------------")"""

    def movement(self, isForward= True):
        """print("Angle: ", self.angle)
        print("Modif X= " + str(self.velocity * math.sin(math.radians(-self.angle))) + "Modif Y= " + str(self.velocity * math.cos(math.radians(-self.angle))))
        print("--------------------------")"""
        self.sprite.center_x += self.velocity * math.sin(math.radians(-self.angle))
        self.sprite.center_y += self.velocity * math.cos(math.radians(-self.angle))
        
    def select_action(self, action):
        if action == DROITE:
            self.rotate(False, self.sprite.position)
        elif action == GAUCHE:
            self.rotate(True, self.sprite.position)
        elif action == AVANT:
            self.movement()
        return action
    
