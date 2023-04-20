import pygame
import random
import numpy as np
from pygame.sprite import *
import math
from pygame.math import *
from Digital_Twin_Software.Agent import *

pygame.font.init()
PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
SCORE_FONT= pygame.font.Font("Software_Game_Assets/PressStart2P-vaV7.ttf", 10)
#SURFACE= pygame.Surface(PLAYER_CAR.get_rect().size, pygame.SRCALPHA)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TREE_WIDTH= 1480 - 820
MAX_WIDTH= 1480
WIDTH_ENV= 820
DROITE= 0
GAUCHE= 1
AVANT= 2

class State():
    def __init__(self, location, agent_angle, parent):
        self.location= location
        self.agent_angle= agent_angle
        self.parent= parent
        self.isWallState= False
    
    def compute_F(self, H, G, WD):
        self.H= H
        self.G= G*0.75
        self.WD= 100000/WD
        self.F= self.H + self.G + self.WD
    
    def set_action_taken(self, action):
        self.action_taken= action

class AStarPathFinding:
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment
        self.known_states = np.array([], dtype= State)  #Closed list
        wd= 10000
        dist_array= np.array([])
        for ele in self.environment.STATIC_SPRITES:
            if ele != self.environment.FINISH_LINE and self.agent.rect.centery >= ele.rect.centery:
                    dist_array= np.append(dist_array, self.euclidian_distance(self.agent.rect.center, ele.rect.center))
        init_state= State(location= self.agent.position, agent_angle= 0, parent= None)
        init_state.compute_F(H= self.euclidian_distance(self.agent.position, self.environment.FINISH_LINE.rect.center), 
                             G= 0, WD= wd)
        init_state.set_action_taken(action= -1)
        self.discovered_states = np.array([init_state], dtype= State) #Open list
    
    def manhattan_distance(self, coord_o, coord_f):
        return abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1])
    
    def euclidian_distance(self, coord_o, coord_f):
        return math.sqrt(abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1]))
    
    
    def get_path(self, state):
        self.path= []
        while state.parent != None:
            self.path= np.insert(self.path, 0, state.action_taken)
            #self.path.append(state.action_taken)
            state= state.parent
        return self.path
    
    def show_path(self, agent, start_state):
        agent_group= Group([agent])
        self.environment.menu.window.fill((255,255,255))
        agent_group.draw(self.environment.menu.window)
        self.environment.STATIC_SPRITES.draw(self.environment.menu.window)
        pygame.display.update()
        path= self.get_path(start_state)
        for action in path:
            _= agent.select_action(action)
            agent_group= Group([agent])
            self.environment.menu.window.fill((255,255,255))
            self.environment.STATIC_SPRITES.draw(self.environment.menu.window)
            agent_group.draw(self.environment.menu.window)
            pygame.display.update()
            for event in pygame.event.get():
                pass
        agent.reset_state()
    
    def isFinalTest(self, agent, state):
        next_state_sprite= Sprite()
        next_state_sprite.rect= agent.image.get_rect()
        next_state_sprite.rect.center= state.location
        rotated_image= pygame.transform.rotate(PLAYER_CAR, state.agent_angle)
        next_state_sprite.rect= rotated_image.get_rect(center= state.location)
        self.collided_sprites= pygame.sprite.spritecollide(next_state_sprite, self.environment.STATIC_SPRITES, False)
        if self.environment.FINISH_LINE in self.collided_sprites and len(self.collided_sprites) > 0:
            return True
        else:
            return False
    
    def isWallCollided(self, agent, state):
        ag= agent
        ag.set_state(state.location, state.agent_angle)
        collided_sprites= pygame.sprite.spritecollide(agent, self.environment.STATIC_SPRITES, False)
        ag_group= Group([ag])
        ag_group.draw(self.environment.menu.window)
        pygame.display.update()
        for event in pygame.event.get():
            pass
        if self.environment.FINISH_LINE not in collided_sprites and len(collided_sprites) > 0:
            ag.kill()
            return True
        else:
            ag.kill()
            return False

    def get_child_states(self, agent, state):
        child_states= np.array([], dtype= State)
        child_dict= agent.take_simulated_actions()
        for child in child_dict:
            child_state= State(location=child_dict[child]["position"], 
                                agent_angle= child_dict[child]["agent_angle"],
                                parent= state)
            child_state.set_action_taken(action= child)
            dist_array= np.array([])
            if not self.isWallCollided(agent, child_state):
                for ele in self.environment.STATIC_SPRITES:
                    if ele != self.environment.FINISH_LINE and child_dict[child]["position"][1] >= ele.rect.centery:
                        dist_array= np.append(dist_array, self.euclidian_distance(ele.rect.center, child_dict[child]["position"]))
                child_state.compute_F(H= self.euclidian_distance(child_dict[child]["position"], self.environment.FINISH_LINE.rect.center), 
                                      G= self.manhattan_distance(state.location, child_dict[child]["position"]), WD= np.sum(dist_array))
                child_states= np.append(child_states, child_state)
            else:
                continue
        return child_states

    def pathfinding(self, agent):
        while len(self.discovered_states) > 0:
            
            current_state= None
            f_min= 100000                           #Valeur d'importance de l'état | F= G+H | G= distance parcourue(etat T --> etat T-1) | H= distance restante(etat T -> etat Final)
            wd_min= 10000
            for state in self.discovered_states:
                if f_min > state.F and not state.isWallState:
                    f_min = state.F
                    current_state = state
            if current_state != None:
                if self.isFinalTest(agent, current_state):
                    return self.get_path(current_state)
                else:
                    agent.set_state(current_state.location, current_state.agent_angle)
                    if current_state in self.discovered_states:
                        self.discovered_states= np.delete(self.discovered_states, np.where(self.discovered_states == current_state))
                    self.known_states= np.append(self.known_states, current_state)
                    agent_group= Group([agent])
                    self.environment.menu.window.fill((255,255,255))
                    agent_group.draw(self.environment.menu.window)
                    self.environment.STATIC_SPRITES.draw(self.environment.menu.window)
                    pygame.display.update()
                    child_states= self.get_child_states(agent, current_state)
                    if len(child_states) == 0:
                        current_state.isWallState= True
                    for child in child_states:
                        if child in self.known_states:  #Si l'état est PLEINEMENT connu, passe au suivant | pas d'optimisation possible
                            continue
                        elif child:                           #Si l'état est PARTIELLEMENT connu, on vérifie si on peut améliorer le chemin en passant par cet état
                            self.discovered_states= np.append(self.discovered_states, child)
                        newG= current_state.G + self.manhattan_distance(current_state.location, child.location)
                        if newG < child.G and child in self.discovered_states:              #Si le chemin est plus court, en passant par cet état, on met à jour l'état
                            child.G= newG
                            child.parent= current_state
                            child.F= child.G + child.H + child.WD
            agent.reset_state()
            self.show_path(agent, current_state)
            
            agent_group= Group([agent])
            self.environment.menu.window.fill((255,255,255))
            agent_group.draw(self.environment.menu.window)
            self.environment.STATIC_SPRITES.draw(self.environment.menu.window)
            pygame.display.update()
            for event in pygame.event.get():
                pass

