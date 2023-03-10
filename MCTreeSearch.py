import pygame
import random
import numpy as np
from pygame.sprite import *

pygame.font.init()
PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
SCORE_FONT= pygame.font.Font("Software_Game_Assets/PressStart2P-vaV7.ttf", 10)
#SURFACE= pygame.Surface(PLAYER_CAR.get_rect().size, pygame.SRCALPHA)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
TREE_WIDTH= 1480 - 820
MAX_WIDTH= 1480
WIDTH_ENV= 820


class ClassicMCTreeSearch():
    def __init__(self, env, agent):
        self.env= env
        self.agent= agent
        self.isFinished= False
        self.finishing_state= None
        self.ui_states= []

    def get_ucb_value(self, state):
        if state.visits == 0:
            return 50
        else:
            return state.wins / state.visits + 2*np.sqrt(np.log(state.parent.visits) / state.visits)

    def get_next_states(self, target_state):
        next_positions= self.agent.take_simulated_actions()
        next_states= []
        for i in next_positions.keys():
            next_state_sprite= Sprite()
            next_state_sprite.rect= self.agent.image.get_rect()
            next_state_sprite.rect.center= next_positions[i]["position"]
            rotated_image= pygame.transform.rotate(PLAYER_CAR, next_positions[i]["agent_angle"])
            next_state_sprite.rect= rotated_image.get_rect(center= next_positions[i]["position"])
            test= pygame.sprite.spritecollide(next_state_sprite, self.env.STATIC_SPRITES, False)
            if len(pygame.sprite.spritecollide(next_state_sprite, self.env.STATIC_SPRITES, False)) > 0:
                continue
            elif next_state_sprite.rect.colliderect(self.env.FINISH_LINE.rect):
                next_states.append(State(parent= target_state, position= next_positions[i]["position"], agent_angle= next_positions[i]["agent_angle"], prev_action= i, environment= self.env, isTerminal= True, isWinningState= True))
            elif next_state_sprite.rect.centery >= 900:
                next_states.append(State(parent= target_state, position= next_positions[i]["position"], agent_angle= next_positions[i]["agent_angle"], prev_action= i, environment= self.env))
            else:
                next_states.append(State(parent= target_state, position= next_positions[i]["position"], agent_angle= next_positions[i]["agent_angle"], prev_action= i, environment= self.env))
        
        return next_states      
    
    #-> Selection= On test le noeud enfant / etat suivant le plus prometteur (meilleure valeur UCB)
    def selection(self, actual_state):         
        max_ucb= -100000
        best_next_state= actual_state
        if len(actual_state.childrens) > 0:
            for next_state in actual_state.childrens:
                if self.get_ucb_value(next_state) > max_ucb:
                    max_ucb= self.get_ucb_value(next_state)
                    best_next_state= next_state
            self.env.show_update(self.agent, best_next_state.position, best_next_state.agent_angle)
            return self.selection(best_next_state)
        else:
            return actual_state
    
    #-> Expansion= On r??cup??re les noeuds enfants / etats suivants du noeud de d??part, jusqu'au dernier connu
    def expansion(self, last_known_state):  
        last_known_state.childrens= self.get_next_states(last_known_state)
        for child in last_known_state.childrens:
            ui_child= UI_State(state= child, mcts= self)
            if ui_child not in self.ui_states:
                self.ui_states.append(ui_child)
        if last_known_state.isTerminal:
            self.finishing_state= last_known_state
            self.isFinished= True
            return last_known_state
        else:
            return self.selection(last_known_state)

    #-> Simulation= On simule un jeu jusqu'?? la fin en prenant des actions randoms pour r??cup??rer le score final
    def simulation(self, target_state):           
        next_states= self.get_next_states(target_state)
        """if len(next_states) > 0:
            target_state.set_childrens(childrens= next_states)"""
        if len(next_states) == 0:
            target_state.set_terminal(isTerminal= True)
            target_state.set_isWinningState(isWinningState= False)
        else:
            selected_state= random.choice(next_states)
        if target_state.isTerminal:
            if target_state.isWinningState:
                return 1
            else:
                return 0
        self.env.show_update(self.agent, selected_state.position, selected_state.agent_angle)
        return self.simulation(selected_state)
    
    #-> Retropropagation= On remonte le score final de la simulation jusqu'au noeud de d??part
    #       | Reset de la position de l'agent(pour d??part d'une nouvelle simulation / cycle d'apprentissage)
    def backpropagation(self, target_state, reward):
        cpt_generation= 0
        if reward == 1:
            color= GREEN
        else:
            color= RED
        while target_state.parent != None:
            cpt_generation += 1
            target_state.wins += reward
            target_state.visits += 1
            for target_ui_state in self.ui_states:
                if target_ui_state.state == target_state:
                    target_ui_state.change_color(color= color)
            target_state= target_state.parent
        target_state.wins += reward
        target_state.visits += 1
        cpt_generation += 1
        print("Dig Generation#", cpt_generation)
        self.env.show_update(self.agent, target_state.position, target_state.agent_angle)
        return target_state

    def get_key_policy(self, state):
        key_policy= ""
        while state.parent != None:
            key_policy= str(state.prev_action) + key_policy
            state= state.parent
        return key_policy
    
    def start_optimization(self):
        initial_state= State(parent= None, position= self.agent.rect.center, agent_angle= self.agent.angle, prev_action= -1, environment= self.env)
        init_ui_state= UI_State(state= initial_state, mcts= self)
        self.ui_states.append(init_ui_state)
        while self.isFinished == False:
            last_known_state= self.selection(initial_state)
            next_state= self.expansion(last_known_state)
            reward= self.simulation(next_state)
            initial_state= self.backpropagation(next_state, reward)
        key_policy= self.get_key_policy(self.finishing_state)
        print("Key_Policy Trouv??e: ", key_policy)
        return key_policy
        


class State():
    def __init__(self, position, agent_angle, parent, prev_action, environment, isTerminal= False, isWinningState= False):
        self.enviroment= environment
        self.parent= parent
        self.childrens= []
        self.isTerminal= isTerminal
        self.wins= 0
        self.position= position
        self.agent_angle= agent_angle
        self.visits= 0
        self.prev_action= prev_action
        self.isWinningState= isWinningState
        self.color= BLUE
    
    def set_childrens(self, childrens):
        self.childrens= childrens
    
    def set_isWinningState(self, isWinningState):
        self.isWinningState= isWinningState
    
    def set_terminal(self, isTerminal):
        self.isTerminal= isTerminal
    
    def get_childrens(self):
        return self.childrens

class UI_State():
    def __init__(self, state, mcts):
        self.state= state
        self.mcts= mcts
        if state.parent == None:
            self.position= (WIDTH_ENV + (TREE_WIDTH / 2), 15)
        
        else:
            for ui_state in self.mcts.ui_states:
                test1= ui_state.state
                test2= self.state.parent
                if ui_state.state == self.state.parent:
                    self.parent_pos= ui_state.position
            if state.prev_action == 0:
                self.position= (WIDTH_ENV + ((self.parent_pos[0] - WIDTH_ENV) / 2), self.parent_pos[1] + 40)
            elif state.prev_action == 1:
                self.position= (self.parent_pos[0], self.parent_pos[1] + 40)
            elif state.prev_action == 2:
                self.position= (self.parent_pos[0] + ((MAX_WIDTH - self.parent_pos[0]) / 2), self.parent_pos[1] + 40)
            test= False
    def draw_state(self,window):
        pygame.draw.circle(window, self.state.color, [self.position[0], self.position[1]], 15)
        # Dessiner le nombre de visites ?? l'int??rieur du cercle
        text = SCORE_FONT.render(str(str(self.state.wins) + "/" + str(self.state.visits)), True, "white")
        text_rect = text.get_rect(center= self.position)
        window.blit(text, text_rect)
    
    def change_color(self, color):
        self.state.color= color
    
    def __eq__(self, other):
        if isinstance(other, UI_State):
            return self.state == other.state
        return False