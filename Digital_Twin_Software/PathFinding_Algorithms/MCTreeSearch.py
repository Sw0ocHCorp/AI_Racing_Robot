import pygame
import random
import numpy as np
from pygame.sprite import *
from math import *

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


class ClassicMCTreeSearch():
    def __init__(self, env, agent):
        self.env= env
        self.agent= agent
        self.isFinished= False
        self.finishing_state= None
        self.ui_states= []
        self.nb_cycle= 0

    def euclidian_distance(self, coord_o, coord_f):
        return sqrt(abs(coord_o[0]-coord_f[0]) + abs(coord_o[1]-coord_f[1]))

    def get_ucb_value(self, state, coeff_explo= 10, coeff_exploit= 10):
        if state.visits == 0:
            state.ucb_value= 20
        else:
            exploit_part= (state.wins / state.visits)
            explo_part= coeff_explo*np.sqrt(np.log(state.parent.visits) / state.visits)
            state.ucb_value= exploit_part + explo_part
        return state.ucb_value

    def get_next_states(self, target_state):
        base_dist= self.euclidian_distance(target_state.position, self.env.FINISH_LINE.rect.center)
        next_positions= self.agent.take_simulated_actions()
        next_states= []
        proba_states= []
        isForward= True
        if abs(next_positions[2]["agent_angle"]) >= 90 and abs(next_positions[2]["agent_angle"]) <= 270:
            isForward= False
        for i in next_positions.keys():
            
            next_state_sprite= Sprite()
            next_state_sprite.rect= self.agent.image.get_rect()
            next_state_sprite.rect.center= next_positions[i]["position"]
            rotated_image= pygame.transform.rotate(PLAYER_CAR, next_positions[i]["agent_angle"])
            next_state_sprite.rect= rotated_image.get_rect(center= next_positions[i]["position"])
            collided_sprites= pygame.sprite.spritecollide(next_state_sprite, self.env.STATIC_SPRITES, False)
            if len(collided_sprites) > 0:
                if self.env.FINISH_LINE in collided_sprites:
                    next_states.append(State(parent= target_state, position= next_positions[i]["position"], agent_angle= next_positions[i]["agent_angle"], prev_action= i, environment= self.env, isTerminal= True, isWinningState= True))
                    if isForward == True:
                        if i == 0 or i == 1:
                            proba_states.append(0.25)
                        elif i == 2:
                            proba_states.append(0.5)
                    else:
                        if i == 0 or i == 1:
                            proba_states.append((1-0.25) / 2)
                        elif i == 2:
                            proba_states.append(0.25)
                else:
                    continue
            elif next_state_sprite.rect.centery >= 900:
                continue
            else:
                next_states.append(State(parent= target_state, position= next_positions[i]["position"], agent_angle= next_positions[i]["agent_angle"], prev_action= i, environment= self.env))
                if isForward == True:
                    if i == 0 or i == 1:
                        proba_states.append(0.25)
                    elif i == 2:
                        proba_states.append(0.5)
                else:
                    if i == 0 or i == 1:
                        proba_states.append((1-0.25) / 2)
                    elif i == 2:
                        proba_states.append(0.25)

        return next_states, proba_states      
    
    #-> Selection= On test le noeud enfant / etat suivant le plus prometteur (meilleure valeur UCB)
    def single_selection(self, actual_state, coeff_explo= 2, coeff_exploit= 2): 
        self.env.clock.tick(20)
        max_ucb= -100000
        best_next_state= actual_state
        for next_state in actual_state.childrens:
            if next_state.isTerminal and next_state.isWinningState:
                best_next_state= next_state
            elif self.get_ucb_value(state= next_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit) > max_ucb:
                if next_state.isTerminal:
                    continue
                else:
                    max_ucb= self.get_ucb_value(next_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit)
                    best_next_state= next_state
        self.env.show_update(self.agent, best_next_state.position, best_next_state.agent_angle, 20)
        return best_next_state
    
    def selection(self, actual_state, coeff_explo= 2, coeff_exploit= 2):  
        self.env.clock.tick(20)       
        best_next_state= actual_state
        while len(best_next_state.childrens) > 0:
            max_ucb= -100000
            for next_state in best_next_state.childrens:
                if next_state.isTerminal and next_state.isWinningState:
                    best_next_state= next_state
                elif self.get_ucb_value(state= next_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit) > max_ucb:
                    if next_state.isTerminal:
                        continue
                    else:
                        max_ucb= self.get_ucb_value(next_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit)
                        best_next_state= next_state
            self.env.show_update(self.agent, best_next_state.position, best_next_state.agent_angle, 20)
        return best_next_state
    
    #-> Expansion= On récupère les noeuds enfants / etats suivants du noeud de départ, jusqu'au dernier connu
    def expansion(self, last_known_state, coeff_explo= 2, coeff_exploit= 2):  
        self.env.clock.tick(20)
        last_known_state.childrens, _= self.get_next_states(last_known_state)
        for child in last_known_state.childrens:
            ui_child= UI_State(state= child, mcts= self)
            if ui_child not in self.ui_states:
                self.ui_states.append(ui_child)
        if last_known_state.isTerminal:
            self.finishing_state= last_known_state
            if last_known_state.isWinningState:
                self.isFinished= True
        else:
            last_known_state= self.single_selection(last_known_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit)
        return last_known_state 

    #-> Simulation= On simule un jeu jusqu'à la fin en prenant des actions randoms pour récupérer le score final
    def simulation(self, target_state):   
        if self.nb_cycle % 10 == 0:
            self.env.clock.tick(45)
        else:
            self.env.clock.tick(200)
        selected_state= target_state
        reward= 0
        isFinished= False
        while isFinished == False:  
            next_states, probas= self.get_next_states(selected_state)
            """if len(next_states) > 0:
                target_state.set_childrens(childrens= next_states)"""
            if len(next_states) == 0:
                selected_state.set_terminal(isTerminal= True)
                selected_state.set_isWinningState(isWinningState= False)
            else:
                rand_val= random.random()
                if len(probas) == 3:
                    if rand_val <= probas[0]:
                        selected_state= next_states[0]
                    elif rand_val <= probas[0] + probas[1]:
                        selected_state= next_states[1]
                    else:
                        selected_state= next_states[2]
                elif len(probas) == 2:
                    if rand_val <= probas[0]:
                        selected_state= next_states[0]
                    else:
                        selected_state= next_states[1]
                else:
                    selected_state= next_states[0]
            if selected_state.isTerminal:
                isFinished= True
                if selected_state.isWinningState:
                    reward= 1
            if self.nb_cycle % 10 == 0:
                print("OK")
                self.env.show_update(self.agent, selected_state.position, selected_state.agent_angle, 45)
            else:
                self.env.show_update(self.agent, selected_state.position, selected_state.agent_angle, 200)
        return reward
    
    #-> Retropropagation= On remonte le score final de la simulation jusqu'au noeud de départ
    #       | Reset de la position de l'agent(pour départ d'une nouvelle simulation / cycle d'apprentissage)
    def backpropagation(self, target_state, reward, coeff_explo, coeff_exploit):
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
        self.env.show_update(self.agent, target_state.position, target_state.agent_angle)
        if reward == 1:
            print("--> " + str(target_state.wins) +" WINS / " + str(target_state.visits) + " VISITS")
            coeff_explo= coeff_explo * 0.9
            coeff_exploit= coeff_exploit *1.1
        return target_state, coeff_explo, coeff_exploit

    def get_key_policy(self, state):
        key_policy= ""
        while state.parent != None:
            key_policy= str(state.prev_action) + key_policy
            self.env.show_update(self.agent, state.position, state.agent_angle, 10)
            state= state.parent
        self.env.show_update(self.agent, state.position, state.agent_angle, 10)
        return key_policy
    
    def start_optimization(self, coeff_explo= 10, coeff_exploit= 10):
        initial_state= State(parent= None, position= self.agent.rect.center, agent_angle= self.agent.angle, prev_action= -1, environment= self.env)
        init_ui_state= UI_State(state= initial_state, mcts= self)
        self.ui_states.append(init_ui_state)
        while self.isFinished == False:
            last_known_state= self.selection(actual_state= initial_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit)
            next_state= self.expansion(last_known_state, coeff_explo= coeff_explo, coeff_exploit= coeff_exploit)
            reward= self.simulation(next_state)
            initial_state, coeff_explo, coeff_exploit= self.backpropagation(next_state, reward, coeff_explo, coeff_exploit= coeff_exploit)
            self.nb_cycle += 1
        key_policy= self.get_key_policy(self.finishing_state)
        print("Key_Policy Trouvée: ", key_policy)
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
        self.ucb_value= 0
    
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
        # Dessiner le nombre de visites à l'intérieur du cercle
        text = SCORE_FONT.render(str(str(self.state.wins) + "/" + str(self.state.visits)), True, BLACK)
        text_rect = text.get_rect(center= self.position)
        window.blit(text, text_rect)
    
    def change_color(self, color):
        self.state.color= color
    
    def __eq__(self, other):
        if isinstance(other, UI_State):
            return self.state == other.state
        return False