import pygame, sys
from pygame.locals import *
import numpy as np
from PIL import Image
import time
import math

from Agent import Agent
from EvolutionaryAlgorithms import GeneticAlgorithm, DifferentialEvolution

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
        self.clock= pygame.time.Clock()
    
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
        first_wall= (0,0)
        last_wall= (0,0)
        target_index= 0
        left_collision= False
        right_collision= False
        for i in range(self.left_bound.shape[0]):
            if min_dist > self.manhattan_distance(agent.hitbox.topleft, self.left_bound[i,:]):
                min_dist= self.manhattan_distance(agent.hitbox.topleft, self.left_bound[i,:])
                target_index= i
        if target_index < self.left_bound.shape[0] - 1:
            first_wall= tuple(self.left_bound[target_index,:])
            last_wall= tuple(self.left_bound[target_index+1,:])
        else:
            first_wall= tuple(self.left_bound[target_index-1,:])
            last_wall= tuple(self.left_bound[target_index,:])
        left_collision= agent.wall_collision(first_wall, last_wall)
        if not left_collision:
            if target_index < self.left_bound.shape[0] - 1 and target_index > 0:
                prev_wall= tuple(self.left_bound[target_index-1,:])
                left_collision= agent.wall_collision(prev_wall, first_wall)
        for i in range(self.right_bound.shape[0]):
            if min_dist > self.manhattan_distance(agent.hitbox.topright, self.right_bound[i,:]):
                min_dist= self.manhattan_distance(agent.hitbox.topright, self.right_bound[i,:])
                target_index= i
        if target_index < self.right_bound.shape[0] - 1:
            first_wall= tuple(self.right_bound[target_index,:])
            last_wall= tuple(self.right_bound[target_index+1,:])
        else:
            first_wall= tuple(self.right_bound[target_index-1,:])
            last_wall= tuple(self.right_bound[target_index,:])
        right_collision= agent.wall_collision(first_wall, last_wall)
        if not right_collision:
            if target_index < self.right_bound.shape[0] - 1 and target_index > 0:
                prev_wall= tuple(self.right_bound[target_index-1,:])
                right_collision= agent.wall_collision(prev_wall, first_wall)
        return left_collision, right_collision
    
    def evaluate_agents(self, agent):
        fitness= 0
        WINDOW.fill((255,255,255))
        WINDOW.blit(agent.skin, agent.hitbox)
        WINDOW.blit(agent.hitbox_surface, agent.surf)
        WINDOW.blit(FINISH_LINE, (400, 0))
        env.draw_walls(isLeft= True)
        env.draw_walls(isLeft= False)
        pygame.display.update()
        i= 0
        while i < len(agent.strategy):
            self.clock.tick(60)
            WINDOW.fill((255,255,255))
            WINDOW.blit(agent.skin, agent.hitbox)
            WINDOW.blit(agent.hitbox_surface, agent.surf)
            WINDOW.blit(FINISH_LINE, (400, 0))
            env.draw_walls(isLeft= True)
            env.draw_walls(isLeft= False)
            pygame.display.update()
            agent.select_action(agent.strategy[i])
            isLeftCollision, isRightCollision= env.capture_wall_collision(agent)
            for event in pygame.event.get():
                pass
            pygame.display.update()
            if (agent.hitbox.top > 900 or agent.hitbox.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                fitness= -150
                break
            elif isLeftCollision or isRightCollision:
                fitness-= 10
            elif agent.position[0] >= 400 and agent.position[0] <= 600 and agent.position[1] <= 24:
                fitness+= 100
                break
            elif fitness <= -150:
                fitness= -150
                break
            else:
                fitness+= 1
            i+= 1
        print("Score_Agent=", fitness)
        return fitness



if __name__ == "__main__":
    env= Environnement()
    ae_agents= np.array([Agent(velocity= 10, rotation_angle= 45, 
                               position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                               skin= "Software_Game_Assets/car1.png") for i in range(5)], dtype= Agent)
    ga= None
    main_agent= Agent(velocity= 10, rotation_angle= 45, position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)))
    run= True
    WINDOW.fill((255,255,255))
    WINDOW.blit(main_agent.skin, main_agent.hitbox)
    WINDOW.blit(FINISH_LINE, (400, 0))
    WINDOW.blit(main_agent.hitbox_surface, main_agent.surf)
    pygame.display.update()
    best_strat= []
    fitness_score= 0
    while run:
        env.clock.tick(3)
        if env.left_bound.shape[0] > 1:
                env.draw_walls(isLeft= True)
        if env.right_bound.shape[0] > 2:
            env.draw_walls(isLeft= False)
            if env.left_bound.shape[0] > 2:
                ga= GeneticAlgorithm(agents= ae_agents, evaluate= env.evaluate_agents)
                best_strat, fitness_score= ga.start_optimization(max_nfe=50)
        if ga is not None:
            if ga.isFinished:
                print("Best_Strat=", best_strat)
                print("Fitness_Score=", fitness_score)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run= False
                break     
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:   # Left click
                    print("Left Wall: ", pygame.mouse.get_pos())       #Dans le Tuple on a (Colonne, Ligne)
                    env.left_bound= np.append(env.left_bound, [pygame.mouse.get_pos()], axis= 0)
                elif event.button == 3: # Right click
                    print("Right Wall: ", pygame.mouse.get_pos())       #Dans le Tuple on a (Colonne, Ligne)
                    env.right_bound= np.append(env.right_bound, [pygame.mouse.get_pos()], axis= 0)
    pygame.quit()