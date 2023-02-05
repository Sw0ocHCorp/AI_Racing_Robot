import pygame, sys
from pygame.locals import *
import numpy as np
from PIL import Image
import time
import math

from Agent import Agent

PURPLE= (137, 0, 255)
PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
FINISH_LINE= pygame.image.load("Software_Game_Assets\Finish_line.png")
player_img= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
HEIGHT= 900
WIDTH= 800
WINDOW= pygame.display.set_mode((WIDTH, HEIGHT))




class Environnement:
    def __init__(self) -> None:
        self.right_bound= np.empty((0,2))
        self.left_bound= np.empty((0,2))

    def attach_agent(self, agent):
        self.agent= agent
    
    def attach_agents(self, agents= np.array([], dtype= Agent)):
        self.agents= agents
    def draw_walls(self, isLeft):
        if isLeft:
            for i in range(1, self.left_bound.shape[0]):
                pygame.draw.line(WINDOW, PURPLE, tuple(self.left_bound[i-1,:]), tuple(self.left_bound[i,:]), 5)
        else:
            for i in range(1, self.right_bound.shape[0]):
                pygame.draw.line(WINDOW, PURPLE, tuple(self.right_bound[i-1,:]), tuple(self.right_bound[i,:]), 5)

    def euclidian_distance(self, coord_o, coord_f):
        return math.sqrt(abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1]))
    
    def manhattan_distance(self, coord_o, coord_f):
        return abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1])

    def capture_wall_collision(self, agent):
        min_dist= 1000
        debut_mur= (0,0)
        fin_mur= (0,0)
        target_index= 0
        left_collision= False
        right_collision= False
        for i in range(self.left_bound.shape[0]):
            if min_dist > self.manhattan_distance(agent.position, self.left_bound[i,:]):
                min_dist= self.manhattan_distance(agent.position, self.left_bound[i,:])
                target_index= i
        if target_index > 0:
            debut_mur= tuple(self.left_bound[target_index-1,:])
            fin_mur= tuple(self.left_bound[target_index,:])
        else:
            debut_mur= tuple(self.left_bound[target_index,:])
            fin_mur= tuple(self.left_bound[target_index+1,:])
        left_collision= agent.wall_collision(debut_mur, fin_mur)
        for i in range(self.right_bound.shape[0]):
            if min_dist > abs((agent.position[0] +agent.position[1]) - (self.right_bound[i, 0] + self.right_bound[i, 1])):
                min_dist= abs((agent.position[0] +agent.position[1]) - (self.right_bound[i, 0] + self.right_bound[i, 1]))
                target_index= i
        if target_index < self.left_bound.shape[0] - 1:
            debut_mur= tuple(self.left_bound[target_index,:])
            fin_mur= tuple(self.left_bound[target_index+1,:])
        else:
            debut_mur= tuple(self.right_bound[target_index-1,:])
            fin_mur= tuple(self.right_bound[target_index,:])
        right_collision= agent.wall_collision(debut_mur, fin_mur)
        return left_collision, right_collision

if __name__ == "__main__":
    env= Environnement()
    agent= Agent(velocity= 10, rotation_vel= 45, position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - PLAYER_HEIGHT))
    env.attach_agent(agent)
    run= True
    clock= pygame.time.Clock()
    #hitbox= agent.rotate(isLeft= True)
    #WINDOW.blit(agent.skin, hitbox.topleft)
    pygame.display.update()
    while run:
        clock.tick(3)
        WINDOW.fill((255,255,255))
        WINDOW.blit(agent.skin, agent.position)
        WINDOW.blit(FINISH_LINE, (400, 0))
        if env.left_bound.shape[0] > 1:
            env.draw_walls(isLeft= True)
        if env.right_bound.shape[0] > 1:
            env.draw_walls(isLeft= False)
            if env.left_bound.shape[0] > 1:
                isLeftCollision, isRightCollision= env.capture_wall_collision(agent)
                print("Left collision: ", isLeftCollision, "Right collision: ", isRightCollision)
                agent.movement(isForward= True)  
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run= False
                break     
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:   # Left click
                    print(pygame.mouse.get_pos())       #Dans le Tuple on a (Colonne, Ligne)
                    env.left_bound= np.append(env.left_bound, [pygame.mouse.get_pos()], axis= 0)
                elif event.button == 3: # Right click
                    env.right_bound= np.append(env.right_bound, [pygame.mouse.get_pos()], axis= 0)
    pygame.quit()