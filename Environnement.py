import pygame, sys
from pygame.locals import *
import numpy as np
from PIL import Image
import time
import math
from pygame.sprite import *
from Agent import Agent
from EvolutionaryAlgorithms import *
from MenuWidget import MenuWidget
from MCTreeSearch import *
import paho.mqtt.client as mqtt
from AStarPathFinding import *

PURPLE= (137, 0, 255)
PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
player_img= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
HEIGHT= 900
WIDTH= 1500
WIDTH_ENV= 800
WINDOW= pygame.display.set_mode((WIDTH, HEIGHT))




class Environnement:
    def __init__(self):
        self.mqtt_client= mqtt.Client(client_id= "AI_Racing_Robot")
        #self.mqtt_client.connect("test.mosquitto.org")
        self.right_bound= np.empty((0,2))
        self.left_bound= np.empty((0,2))
        self.clock= pygame.time.Clock()
        self.num_lwall= 0
        self.num_rwall= 0
        self.prev_left_position= None
        self.prev_right_position= None
        self.best_dist= 1000
        self.stop_eval= False
        self.menu= MenuWidget(WINDOW)
        self.isAlive= False
        self.STATIC_SPRITES= Group()
        self.FINISH_LINE= Sprite(self.STATIC_SPRITES)
        self.FINISH_LINE.image= pygame.image.load("Software_Game_Assets\Finish_line.png")
        self.FINISH_LINE.rect= self.FINISH_LINE.image.get_rect()
        self.FINISH_LINE.rect.topleft= (400, 0)
        self.key_policy= ""
        self.clock.tick(10)

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
                    self.STATIC_SPRITES.add(wall)
            self.prev_left_position= pos
        elif isLeft == False:
            if self.prev_right_position != None:
                self.num_rwall += 1
                for position in self.bresenham_algorithm(self.prev_right_position, pos):
                    wall= Sprite()
                    wall.image= pygame.image.load("Software_Game_Assets\wall.png")
                    wall.rect= wall.image.get_rect()
                    wall.rect.center= position
                    self.STATIC_SPRITES.add(wall)
            self.prev_right_position= pos
        self.STATIC_SPRITES.draw(WINDOW)
        self.menu.draw_menu()
        pygame.display.update()
        for event in pygame.event.get():
            pass
        print("Left wall: ", self.num_lwall)
        print("Right wall: ", self.num_rwall)

    #-> FONCTION MARCHANT AVEC LE GA
    def multi_eval_agents(self, agents):
        agents_group= Group([agent for agent in agents])
        stop_eval_array= [False for i in range(len(agents))]
        self.clock.tick(20)
        fitness= np.zeros(len(agents))
        #WINDOW.fill((51,51,51))
        WINDOW.fill((255,255,255))
        pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
        self.STATIC_SPRITES.draw(WINDOW)
        self.menu.draw_menu()
        agents_group.draw(WINDOW)
        pygame.display.update()
        for i in range(len(agents[0].strategy)):
            for j, agent in enumerate(agents):
                if stop_eval_array[j] == False:
                    action= agent.select_action(agent.strategy[i])
                    collided_sprites= pygame.sprite.spritecollide(agent, self.STATIC_SPRITES, False)
                    if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))
                        stop_eval_array[j]= True
                    elif len(collided_sprites) != 0 and self.FINISH_LINE not in collided_sprites:
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))
                        stop_eval_array[j]= True
                    elif self.FINISH_LINE in collided_sprites:
                        stop_eval_array[j]= True
                    else:
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))
                else:
                    continue
                if np.count_nonzero(stop_eval_array) == len(stop_eval_array):
                    break
            if np.count_nonzero(stop_eval_array) == len(stop_eval_array):
                break
                #WINDOW.fill((51,51,51))
            WINDOW.fill((255,255,255))
            pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
            self.STATIC_SPRITES.draw(WINDOW)
            self.menu.draw_menu()
        print("Fitness évaluées= ", np.sort(fitness))
        return fitness
    
    def bi_objective_eval_agents(self, agents):
        agents_group= Group([agent for agent in agents])
        stop_eval_array= [False for i in range(len(agents))]
        fitness= np.zeros(len(agents))
        steps= np.array([len(agents[0].strategy) for i in range(len(agents))])
        #WINDOW.fill((51,51,51))
        WINDOW.fill((255,255,255))
        pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
        self.STATIC_SPRITES.draw(WINDOW)
        self.menu.draw_menu()
        agents_group.draw(WINDOW)
        pygame.display.update()
        for i in range(len(agents[0].strategy)):
            for j, agent in enumerate(agents):
                if stop_eval_array[j] == False:
                    action= agent.select_action(agent.strategy[i])
                    steps[j]= i+1
                    collided_sprites= pygame.sprite.spritecollide(agent, self.STATIC_SPRITES, False)
                    if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))  
                        stop_eval_array[j]= True
                        steps[j]= 100
                    elif len(collided_sprites) != 0 and self.FINISH_LINE not in collided_sprites:
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))
                        stop_eval_array[j]= True
                        steps[j]= 100 - steps[j]
                    elif self.FINISH_LINE in collided_sprites:
                        stop_eval_array[j]= True
                    else:
                        fitness[j]= self.manhattan_distance(agent.rect.center, (500, 24))
                else:
                    continue
                if np.count_nonzero(stop_eval_array) == len(stop_eval_array):
                    break
            if np.count_nonzero(stop_eval_array) == len(stop_eval_array):
                break
                #WINDOW.fill((51,51,51))
            WINDOW.fill((255,255,255))
            pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
            self.STATIC_SPRITES.draw(WINDOW)
            self.menu.draw_menu()
        print("Fitness évaluées= ", np.concatenate((np.reshape(steps[:len(agents) // 2], (-1, 1)), np.reshape(fitness[:len(agents) // 2], (-1, 1))), axis=1))
        
        return steps, fitness

    #-> FONCTION MARCHANT AVEC LE GA
    def evaluate_agent(self, agent):
        agent_group= Group([agent])
        #self.clock.tick(60)
        fitness= 0
        #WINDOW.fill((51,51,51))
        WINDOW.fill((255,255,255))
        pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
        agent_group.draw(WINDOW)
        self.STATIC_SPRITES.draw(WINDOW)
        self.menu.draw_menu()
        self.menu.show_init_agents()
        self.menu.show_new_agents()
        for i in range(0, len(agent.strategy)):
            action= agent.select_action(agent.strategy[i])
            collided_sprites= pygame.sprite.spritecollide(agent, self.STATIC_SPRITES, False)
            if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                fitness= -500
            elif len(collided_sprites) != 0 and self.FINISH_LINE not in collided_sprites:
                fitness-= 50
                self.stop_eval= True
            elif self.FINISH_LINE in collided_sprites:
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
            #WINDOW.fill((51,51,51))
            WINDOW.fill((255,255,255))
            agent_group.draw(WINDOW)
            self.STATIC_SPRITES.draw(WINDOW)
            self.menu.draw_menu()
            self.menu.show_init_agents()
            self.menu.show_new_agents()
            pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
            pygame.display.update()
            for event in pygame.event.get():
                pass
        return fitness

    def send_optimum_strategy(self, best_strat):
        mqtt_message=""
        for action in best_strat:
            mqtt_message+= str(int(action))
        self.mqtt_client.publish("AI_RACING_Robot/Best_Strategy", mqtt_message)
        time.sleep(1)
    
    def send_key_policy(self, key_policy):
        mqtt_message=""
        for action in best_strat:
            mqtt_message= key_policy
        self.mqtt_client.publish("AI_RACING_Robot/Best_Strategy", mqtt_message)
        time.sleep(1)

    def show_update(self, agent, position, angle, framerate= 30):
        self.clock.tick(framerate)
        agent.set_state(position, angle)
        group_agent= Group([agent])
        WINDOW.fill((255,255,255))
        group_agent.draw(WINDOW)
        self.STATIC_SPRITES.draw(WINDOW)
        self.menu.draw_mcts_menu()
        pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
        pygame.display.update()

        for event in pygame.event.get():
            self.clock.tick(framerate)
            pass


if __name__ == "__main__":
    canWritePop= False
    canWriteNfe= False
    ae_agents= []
    env= Environnement()
    ga= None
    run= True
    main_agent= Agent(velocity= 20, rotation_angle= 45, position= ((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)))
    #WINDOW.fill((51,51,51))
    WINDOW.fill((255,255,255))
    pygame.draw.line(WINDOW, (0,0,0), (WIDTH_ENV, 0), (WIDTH_ENV, HEIGHT), 5)
    main_agent.draw(WINDOW)
    env.STATIC_SPRITES.draw(WINDOW)
    env.menu.draw_menu()
    best_strat= []
    fitness_score= 0
    isPrinted= False
    ga= None
    nsga2= None
    mcts_algorithm= None
    astar_algorithm= None
    best_indiv= None
    pygame.display.update()
    while run:
        env.clock.tick(10)
        env.STATIC_SPRITES.draw(WINDOW)
        env.menu.draw_menu()
        if env.isAlive:
            """if mcts_algorithm is None:
                mcts_algorithm= ClassicMCTreeSearch(env= env, agent= main_agent)
                env.menu.attach_mcts_algo(mcts_algorithm)
                env.key_policy= mcts_algorithm.start_optimization(coeff_explo= 5, coeff_exploit= 50)
                env.isAlive= False"""
            """if ga is None:
                #ga= GeneticAlgorithm(agents= main_agent, evaluate= env.evaluate_agent)
                ae_agents= [Agent(velocity= 20, rotation_angle= 45, 
                                position= ((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                skin= "Software_Game_Assets/car1.png") for i in range(int(env.menu.pop_buffer))]
                ga= GeneticAlgorithm(agents= ae_agents, environment= env, evaluate= env.multi_eval_agents, isThreadEvaluation= True)
                ga.set_max_nfe(int(env.menu.nfe_buffer))
                ga.attach_menu(env.menu)
                env.menu.attach_ga(ga)"""
            """if nsga2 is None:
                ae_agents= [Agent(velocity= 20, rotation_angle= 45, 
                                position= ((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                skin= "Software_Game_Assets/car1.png") for i in range(int(env.menu.pop_buffer))]
                nsga2= NSGAII(agents= ae_agents, n_obj_evaluate= env.bi_objective_eval_agents, environment= env, menu= env.menu, max_nfe= int(env.menu.nfe_buffer))
            best_indiv= nsga2.start_optimization()"""
            if astar_algorithm is None:
                astar_algorithm= AStarPathFinding(environment= env, agent= main_agent)
                best_strat= astar_algorithm.pathfinding(astar_algorithm.agent)
                env.isAlive= False
            #env.evaluate_agent(main_agent)
            isPrinted= False
            #best_strat, fitness_score= ga.start_optimization()
        """if ga is not None:
            if ga.isFinished and isPrinted == False:
                isPrinted= True
                env.isAlive= False
                for action in best_strat:
                    _= main_agent.select_action(best_strat)
                print("Best_Strat=", best_strat)
                print("Fitness_Score=", fitness_score)"""
        """if nsga2 is not None:
            if nsga2.isFinished and isPrinted == False:
                isPrinted= True
                env.isAlive= False
                assert best_indiv is not None
                best_strat= best_indiv["strategy"]
                for action in best_strat:
                    _= main_agent.select_action(best_strat)
                print("Best_Strat=", best_strat)
                print("Steps_Score=", best_indiv["steps_score"], "Global_Score=", best_indiv["global_score"])"""
        pygame.display.update()

        for event in pygame.event.get():
            env.clock.tick(10)
            if event.type == pygame.QUIT:
                run= False
                break     
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:   # Left click 
                    if (env.menu.robot_pb_interaction(pygame.mouse.get_pos()) == False) or (env.menu.experiment_pb_interaction(pygame.mouse.get_pos()) == False):
                        if env.menu.pop_entry_interaction(pygame.mouse.get_pos()) == True:
                            canWritePop= True
                            canWriteNfe= False
                        elif env.menu.nfe_entry_interaction(pygame.mouse.get_pos()) == True:
                            canWriteNfe= True
                            canWritePop= False
                        elif env.menu.robot_pb_interaction(pygame.mouse.get_pos()) == True:
                                if ga is not None and ga.isFinished == True:
                                    env.send_optimum_strategy(best_strat)
                                env.send_key_policy(key_policy= env.key_policy)
                        elif env.menu.experiment_pb_interaction(pygame.mouse.get_pos()) == True:
                            if ga is not None and ga.isFinished == True:
                                ae_agents= [Agent(velocity= 10, rotation_angle= 45, 
                                                position= ((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                                skin= "Software_Game_Assets/car1.png") for i in range(int(env.menu.pop_buffer))]
                                ga= GeneticAlgorithm(agents= ae_agents, environment= env, evaluate= env.multi_eval_agents, isThreadEvaluation= True)
                                ga.set_max_nfe(env.menu.nfe_buffer)
                            env.isAlive= True
                            canWritePop= False
                            canWriteNfe= False
                        else:
                            if pygame.mouse.get_pos()[0] < WIDTH_ENV:
                                env.build_wall(isLeft= True, pos= pygame.mouse.get_pos())
                    else:
                        canWriteNfe= False
                        canWritePop= False
                elif event.button == 3: # Right click   
                    collide_pop_entry= env.menu.pop_entry_interaction(pygame.mouse.get_pos())
                    collide_nfe_entry= env.menu.nfe_entry_interaction(pygame.mouse.get_pos())
                    collide_robot_pb= env.menu.robot_pb_interaction(pygame.mouse.get_pos())
                    collide_experiment_pb= env.menu.experiment_pb_interaction(pygame.mouse.get_pos()) 
                    if collide_pop_entry == False and collide_nfe_entry == False and collide_robot_pb == False and collide_experiment_pb == False:
                        if pygame.mouse.get_pos()[0] < WIDTH_ENV:
                            env.build_wall(isLeft= False, pos= pygame.mouse.get_pos())  #Dans le Tuple on a (Colonne, Ligne)

            elif event.type == pygame.KEYDOWN:
                if canWritePop == True:
                    if event.key == pygame.K_BACKSPACE:
                        env.menu.pop_backspace()
                    else:
                        env.menu.pop_write_text(event.unicode) 
                if canWriteNfe == True:
                    if event.key == pygame.K_BACKSPACE:
                        env.menu.nfe_backspace()
                    else:
                        env.menu.nfe_write_text(event.unicode)     

    pygame.quit()