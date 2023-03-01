import pygame, sys
from pygame.locals import *
import numpy as np
from PIL import Image
import time
import math
from pygame.sprite import *
from Agent import Agent
from EvolutionaryAlgorithms import GeneticAlgorithm, DifferentialEvolution, GARatingThread

PURPLE= (137, 0, 255)
PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
STATIC_SPRITES= Group()
FINISH_LINE= Sprite(STATIC_SPRITES)
FINISH_LINE.image= pygame.image.load("Software_Game_Assets\Finish_line.png")
FINISH_LINE.rect= FINISH_LINE.image.get_rect()
FINISH_LINE.rect.topleft= (400, 0)
player_img= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
HEIGHT= 900
WIDTH= 800
WINDOW= pygame.display.set_mode((WIDTH, HEIGHT))




class Environnement:
    def __init__(self, agents_to_optimize):
        self.right_bound= np.empty((0,2))
        self.left_bound= np.empty((0,2))
        self.clock= pygame.time.Clock()
        self.agents= Group()
        self.num_lwall= 0
        self.num_rwall= 0
        self.prev_left_position= None
        self.prev_right_position= None
        self.best_dist= 1000
        self.stop_eval= False
        self.agents= Group()
        for agent in agents_to_optimize:
            self.agents.add(agent)

    def euclidian_distance(self, coord_o, coord_f):
        return math.sqrt(abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1]))
    
    def manhattan_distance(self, coord_o, coord_f):
        return abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1])
    
    def bresenham_algorithm(self, first_point, last_point):
        coords= np.empty((0,2))
        new_point= []
        fp_tuple= None
        lp_tuple= None
        # Détermination de la direction de la ligne
        steep = last_point[1] - first_point[1] > 0 or last_point[0] - first_point[0] > 0
        isFlip= False
        # S'assurer que la ligne se dessine de gauche à droite
        if first_point[0] > last_point[0] or first_point[1] > last_point[1]:
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
    
    def build_wall(self, isLeft, pos):
        if isLeft == True:
            if self.prev_left_position != None:
                self.num_lwall += 1
                for position in self.bresenham_algorithm(self.prev_left_position, pos):
                    wall= Sprite()
                    wall.image= pygame.image.load("Software_Game_Assets\wall.png")
                    wall.rect= wall.image.get_rect()
                    wall.rect.center= position
                    STATIC_SPRITES.add(wall)
            self.prev_left_position= pos
        elif isLeft == False:
            if self.prev_right_position != None:
                self.num_rwall += 1
                for position in self.bresenham_algorithm(self.prev_right_position, pos):
                    wall= Sprite()
                    wall.image= pygame.image.load("Software_Game_Assets\wall.png")
                    wall.rect= wall.image.get_rect()
                    wall.rect.center= position
                    STATIC_SPRITES.add(wall)
            self.prev_right_position= pos
        STATIC_SPRITES.draw(WINDOW)
        pygame.display.update()
        for event in pygame.event.get():
            pass
        print("Left wall: ", self.num_lwall)
        print("Right wall: ", self.num_rwall)

    def multi_eval_agents(self, agents):
        agents_group= Group([agent for agent in agents])
        stop_eval_array= [False for i in range(len(agents))]
        self.clock.tick(3)
        fitness= np.zeros(len(agents))
        WINDOW.fill((255,255,255))
        agents_group.draw(WINDOW)
        STATIC_SPRITES.draw(WINDOW)
        for i in range(len(agents[0].strategy)):
            for j, agent in enumerate(agents):
                if stop_eval_array[j] == False:
                    action= agent.select_action(agent.strategy[i])
                    collided_sprites= pygame.sprite.spritecollide(agent, STATIC_SPRITES, False)
                    if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                        fitness[j]= -500
                    elif len(collided_sprites) != 0 and FINISH_LINE not in collided_sprites:
                        fitness[j]-= 50
                        stop_eval_array[j]= True
                    elif FINISH_LINE in collided_sprites:
                        fitness[j]+= 2000
                        stop_eval_array[j]= True
                    if fitness[j] <= -500:
                            stop_eval_array[j]= True
                    else:
                        agent_dist= self.manhattan_distance(agent.rect.center, (500, 24))
                        if self.best_dist >= agent_dist:
                            self.prev_dist= agent_dist
                            fitness[j]+= 50
                            if action == 2:
                                fitness[j]+= 10
                            else:
                                fitness[j]+= 5
                        else:
                            fitness[j]-= 3
                            if action == 2:
                                fitness[j]+= 10
                            else:
                                fitness[j]+= 5
                else:
                    continue
                WINDOW.fill((255,255,255))
                STATIC_SPRITES.draw(WINDOW)
                agents_group.draw(WINDOW)
                pygame.display.update()
                for event in pygame.event.get():
                    pass
        print("Fitness évaluées= ", fitness)
        return fitness

    def evaluate_agent(self, agent):
        self.clock.tick(60)
        fitness= 0
        WINDOW.fill((255,255,255))
        agent.draw(WINDOW)
        STATIC_SPRITES.draw(WINDOW)
        for i in range(0, len(agent.strategy)):
            action= agent.select_action(agent.strategy[i])
            collided_sprites= pygame.sprite.spritecollide(agent, STATIC_SPRITES, False)
            if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                fitness= -500
            elif len(collided_sprites) != 0 and FINISH_LINE not in collided_sprites:
                fitness-= 50
                self.stop_eval= True
            elif FINISH_LINE in collided_sprites:
                fitness+= 2000
                self.stop_eval= True
            if fitness <= -500:
                    self.stop_eval= True
            else:
                agent_dist= self.manhattan_distance(agent.rect.center, (500, 24))
                if self.best_dist >= agent_dist:
                    self.prev_dist= agent_dist
                    fitness+= 50
                    if action == 2:
                        fitness+= 10
                    else:
                        fitness+= 5
                else:
                    fitness-= 3
                    if action == 2:
                        fitness+= 10
                    else:
                        fitness+= 5
            WINDOW.fill((255,255,255))
            agent.draw(WINDOW)
            STATIC_SPRITES.draw(WINDOW)
            pygame.display.update()
            for event in pygame.event.get():
                pass
        return fitness



if __name__ == "__main__":
    ae_agents= [Agent(velocity= 10, rotation_angle= 45, 
                               position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                               skin= "Software_Game_Assets/car1.png") for i in range(10)]
    env= Environnement(agents_to_optimize= ae_agents)
    ga= None
    main_agent= Agent(velocity= 10, rotation_angle= 45, position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)))
    run= True
    WINDOW.fill((255,255,255))
    env.agents.draw(WINDOW)
    STATIC_SPRITES.draw(WINDOW)
    best_strat= []
    fitness_score= 0
    isPrinted= False
    ga= None
    pygame.display.update()
    while run:
        env.clock.tick(3)
        STATIC_SPRITES.draw(WINDOW)
        if env.num_lwall > 3:
            if env.num_rwall > 3:
                if ga is None:
                    #ga= GeneticAlgorithm(agents= ae_agents, evaluate= env.evaluate_agent)
                    ga= GeneticAlgorithm(agents= ae_agents, evaluate= env.multi_eval_agents, isThreadEvaluation= True)
                    if ga.isFinished == False:
                        best_strat, fitness_score= ga.start_optimization(max_nfe=200)
        if ga is not None:
            if ga.isFinished and isPrinted == False:
                isPrinted= True
                print("Best_Strat=", best_strat)
                print("Fitness_Score=", fitness_score)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run= False
                break     
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:   # Left click      
                    env.build_wall(isLeft= True, pos= pygame.mouse.get_pos())   #Dans le Tuple on a (Colonne, Ligne)
                elif event.button == 3: # Right click    
                    env.build_wall(isLeft= False, pos= pygame.mouse.get_pos())  #Dans le Tuple on a (Colonne, Ligne)
    pygame.quit()