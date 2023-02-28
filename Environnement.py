import arcade
import numpy as np
from PIL import Image
import time
import math
from fractions import Fraction

from Agent import Agent
from EvolutionaryAlgorithms import GeneticAlgorithm, DifferentialEvolution, GARatingThread

HEIGHT= 900
WIDTH= 800
PLAYER_CAR= arcade.Sprite("Software_Game_Assets\Player_car_final.png", 1)
FINISH_LINE= arcade.Sprite("Software_Game_Assets\Finish_line.png", 1)
PLAYER_IMG= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= PLAYER_IMG.size




class Environnement(arcade.Window):
    def __init__(self, isMultiThread= False):
        super().__init__(WIDTH, HEIGHT, "Software")
        arcade.set_background_color(arcade.color.WHITE)
        FINISH_LINE.center_x= 500
        FINISH_LINE.center_y= HEIGHT - 12
        self.agents= arcade.SpriteList()
        self.offspring_agents= arcade.SpriteList()
        self.off_agent_array= np.array([], dtype= Agent)
        self.wall_list= arcade.SpriteList(use_spatial_hash= True)
        self.prev_left_position= None
        self.prev_right_position= None
        self.isMultiThread= isMultiThread
        self.num_lwall= 0
        self.num_rwall= 0
        self.index_stat= 0
        self.index_agent= 0
        self.action_strat= 0
        self.ok= False
        self.prev_dist= 1000
        # ==> Booléens pour contrôler l'exécution du GA
        self.finish= False
        self.isFirstEval= False
        self.isOffspringCreated= False
        self.isEvaluated= False
        self.isReplacementDone= False
    # ===> FONCTION API OBSERVERS (Arcade) <=== #
    def setup(self):
        self.ae_agents= np.array([Agent(velocity= 10, rotation_angle= 45, 
                                position= ((WIDTH/2) - (PLAYER_WIDTH / 2), (PLAYER_HEIGHT/1.7)),
                                skin= "Software_Game_Assets/car1.png") for i in range(10)], dtype= Agent)
        self.agents_array= self.ae_agents.copy()
        self.ga= GeneticAlgorithm(self.ae_agents)
        self.evaluation_array= np.array([GARatingThread(agent, self) for agent in self.ae_agents], dtype= GARatingThread)
        self.main_agent= Agent(velocity= 10, rotation_angle= 45, position= ((WIDTH/2) - (PLAYER_WIDTH / 2), (PLAYER_HEIGHT/1.7)))
        self.main_sprite= self.main_agent.sprite
        self.agent_actions= np.zeros(len(self.ae_agents))
        self.agent_fitness= np.zeros(len(self.ae_agents))
        self.offspring_fitness= np.zeros(len(self.ae_agents)*2)
        #self.fitness= 0
        for agent in self.ae_agents:
            self.agents.append(agent.sprite)

    def on_draw(self):
        self.clear()
        FINISH_LINE.draw()
        #Décommenter pour test sur un seul Agent
        """self.main_sprite.draw()
        self.main_sprite.draw_hit_box(arcade.color.RED, 3)"""

        #Commenter pour Fonctionnement normal
        if self.isFirstEval == False:
            self.agents.draw()
            self.agents.draw_hit_boxes(arcade.color.RED, 3)
        elif self.isEvaluated == False:
            self.offspring_agents.draw()
            self.offspring_agents.draw_hit_boxes(arcade.color.RED, 3)

        self.wall_list.draw()
        time.sleep(0.3)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.prev_left_position != None:
                self.num_lwall += 1
                for position in self.bresenham_algorithm(self.prev_left_position, (x, y)):
                    wall= arcade.Sprite("Software_Game_Assets\wall.png", 1)
                    wall.center_x= position[0]
                    wall.center_y= position[1]
                    self.wall_list.append(wall)
            self.prev_left_position= (x, y)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.prev_right_position != None:
                self.num_rwall += 1
                for position in self.bresenham_algorithm(self.prev_right_position, (x, y)):
                    wall= arcade.Sprite("Software_Game_Assets\wall.png", 1)
                    wall.center_x= position[0]
                    wall.center_y= position[1]
                    self.wall_list.append(wall)
            self.prev_right_position= (x, y)
        print("Left wall: ", self.num_lwall)
        print("Right wall: ", self.num_rwall)
    
    def on_update(self, frame_rate= 1/1):
        if self.num_lwall >= 4 and self.num_rwall >= 4:
            if self.ga.limit_nfe >= 0:
                # --> Lancement du GA | Evaluation de la GEN#0
                if self.isFirstEval == False:
                    #Test evaluation d'un seul Agent
                    """if self.action_strat < len(self.main_agent.strategy):
                        self.fitness+= self.evaluate_agent(self.main_agent, self.action_strat)
                    else:
                        print("Fitness: ", self.fitness)
                    self.action_strat+= 1"""
                    #Fontionnement normal
                    if self.action_strat < len(self.agents_array[0].strategy):
                        if self.index_agent < len(self.agents):
                            self.agent_fitness[self.index_agent]+= self.evaluate_agent(self.ae_agents[self.index_agent], self.action_strat)
                            self.index_agent+= 1
                        else:
                            self.index_agent= 0
                        self.action_strat+= 1
                    else:
                        print("----------------------------------")
                        print("==> Evaluation de la GEN#0 !")
                        print(self.agent_fitness)
                        print("----------------------------------")
                        self.ga.limit_nfe -= len(self.agents)
                        self.ga.set_pop_fitness(self.agent_fitness)
                        self.agent_fitness= np.zeros(len(self.agents))
                        self.isFirstEval= True
                        self.index_agent= 0
                        self.action_strat= 0
                # --> Création des Enfants & Distribution des stratégies
                elif self.isOffspringCreated == False:
                    offspring_strategies= self.ga.create_offspring()
                    offspring_agents= self.ga.distribute_strategies(offspring_strategies)
                    self.ga.set_offspring_stategies(offspring_strategies)
                    self.offspring_agents.clear()
                    for agent in offspring_agents:
                        self.offspring_agents.append(agent.sprite)
                    self.off_agent_array= offspring_agents.copy()
                    self.isOffspringCreated= True
                # --> Evaluation des Enfants
                elif self.isEvaluated == False:
                    if self.action_strat < len(self.off_agent_array[0].strategy):
                        if self.index_agent < len(self.offspring_agents):
                            self.offspring_fitness[self.index_agent]+= self.evaluate_agent(self.off_agent_array[self.index_agent], self.action_strat)
                            self.index_agent+= 1
                        else:
                            self.index_agent= 0
                        self.action_strat+= 1
                    else:
                        print("----------------------------------")
                        print("==> Evaluation des Enfants Terminée !")
                        print(self.offspring_fitness)
                        print("----------------------------------")
                        self.ga.limit_nfe -= len(self.offspring_agents)
                        self.ga.set_offspring_fitness(self.offspring_fitness)
                        self.offspring_fitness= np.zeros(len(self.offspring_agents))
                        self.isEvaluated= True
                        self.index_agent= 0
                        self.action_strat= 0
                # --> Eugénisme & Selection des meilleurs Agents pour constituer la GEN#X+1
                elif self.isReplacementDone == False:
                    new_fitness= self.ga.replacement()
                    self.ga.set_pop_fitness(new_fitness)
                    new_agents= self.ga.distribute_strategies(self.ga.population)
                    self.agents.clear()
                    for agent in new_agents:
                        self.agents.append(agent.sprite)
                    self.agents_array= new_agents.copy()
                    self.off_agent_array= np.array([], dtype= Agent)
                    self.isReplacementDone= True
                else:
                    self.isOffspringCreated= False
                    self.isEvaluated= False
                    self.isReplacementDone= False
                    self.index_agent= 0
                    self.action_strat= 0
            else:

                print("Max Fitness: ", self.ga.fitness[np.argmax(self.ga.fitness)])
        self.agents.on_update(frame_rate)
        self.offspring_agents.on_update(frame_rate)
        

    #Fonction Developeur
    def thread_evaluate_agents(self, agents, i):
        pass

    def evaluate_agent(self, agent, i):
        fitness= 0
        action= agent.select_action(agent.strategy[i])
        if arcade.check_for_collision_with_list(agent.sprite, self.wall_list):
            fitness-= 50
        if ((agent.sprite.center_y - (PLAYER_HEIGHT/2)) <= 0 or (agent.sprite.center_y + (PLAYER_HEIGHT/2)) > 900):
            fitness= -500
            self.finish= True
        elif arcade.check_for_collision(agent.sprite, FINISH_LINE):
            fitness+= 2000
            self.finish= True
        if fitness <= -500:
            self.finish= True
        else:
            agent_dist= arcade.get_distance_between_sprites(agent.sprite, FINISH_LINE)
            if self.prev_dist >= agent_dist:
                self.prev_dist= agent_dist
                fitness= 50
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
        return fitness    

    
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
            if first_point[1] > last_point[1]:
                fp_tuple= (last_point[0], last_point[1])
                lp_tuple= (first_point[0], first_point[1])
            if fp_tuple is not None and lp_tuple is not None:
                first_point= fp_tuple
                last_point= lp_tuple
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
    

if __name__ == "__main__":
    env = Environnement()
    env.setup()
    arcade.run()