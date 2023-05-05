import pygame
from Agent import ReinforcementAgent
from PIL import Image
import numpy as np
import math
import time
import copy


DROITE= 0
GAUCHE= 1
AVANT= 2

PLAYER_CAR= pygame.image.load("Digital_Twin_Software\Software_Game_Assets\Player_car_final.png")
player_img= Image.open("Digital_Twin_Software\Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
HEIGHT= 940
WIDTH= 1500
WIDTH_ENV= 800
WINDOW= pygame.display.set_mode((WIDTH, HEIGHT))


class QLearningAlgorithm():
    def __init__(self, environment, nb_agents= 1):
        self.super_brain= {}
        self.env= environment
        self.agents= []
        for i in range(nb_agents):
            self.agents.append(ReinforcementAgent(self.env, velocity= 30, rotation_angle= 45))
    def select_opti_action(self, position, angle, agent, exploration_rate= 0.25):
        rewards= self.super_brain[position]["rewards"]
        actions_possible= []
        rand_value= np.random.rand()
        if np.max(rewards) == 0:
            for i, r in enumerate(rewards):
                nxt_l, nxt_an= agent.simulated_take_action(position, angle, i)
                nxt_r= agent.get_state_reward(nxt_l, nxt_an, 0)
                if r >= 0 and any(val>=0 for val in nxt_r):
                    actions_possible.append(i)
            if len(actions_possible) == 0:
                return np.random.randint(0, len(rewards))
            else :
                return np.random.choice(actions_possible)
        elif rand_value < exploration_rate:
            return np.random.randint(0, len(rewards))
        else:
            return np.argmax(rewards)
    
    def update_brain(self, next_locs, locs, rewards, actions, controller, alpha= 0.35, gamma= 0.9):
        conflict_indexs= []
        corrects_indexs= []
        garbage_indexs= []
        correct_pos= []
        for i, l in enumerate(locs):
            if controller[i] == True:
                garbage_indexs.append(i)
            elif l not in correct_pos:
                correct_pos.append(l)
                corrects_indexs.append(i)
            else:
                conflict_indexs.append(i)
        updated_rewards= [-1000 for i in range(len(locs))]
        for i, loc in enumerate(locs):
            if i not in garbage_indexs:
                if rewards[i] == -1:
                    updated_rewards[i]= rewards[i]
                    self.agents[i].brain[loc]["rewards"][actions[i]]= updated_rewards[i]
                else:
                    future_rewards= self.agents[i].brain[next_locs[i]]["rewards"]
                    updated_rewards[i]= ((1-alpha) * self.super_brain[loc]["rewards"][actions[i]]) + alpha*(rewards[i] + gamma * np.max(future_rewards))
                    self.agents[i].brain[loc]["rewards"][actions[i]]= updated_rewards[i]
        min_reward= -1000
        for i in conflict_indexs:
            if updated_rewards[i] > min_reward:
                min_reward= updated_rewards[i]
                if updated_rewards[i] > 0:
                    r= 255 - (100 * updated_rewards[i])
                    if r < 0:
                        r= 0
                    elif r > 255:
                        r= 255
                    if "hitbox" not in self.super_brain[locs[i]].keys():
                        hitbox= pygame.Surface((PLAYER_WIDTH, PLAYER_WIDTH), pygame.SRCALPHA)
                        hitbox.fill((r, 255, 0))
                        self.super_brain[locs[i]]["hitbox"]= hitbox
                    else:
                        self.super_brain[locs[i]]["hitbox"].fill((r, 255, 0))
                self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]
        for i in corrects_indexs:
            if updated_rewards[i] > 0:
                r= 255 - (100 * 1-updated_rewards[i])
                if r < 0:
                    r= 0
                elif r > 255:
                    r= 255
                if "hitbox" not in self.super_brain[locs[i]].keys():
                    hitbox= pygame.Surface((PLAYER_WIDTH, PLAYER_WIDTH), pygame.SRCALPHA)
                    hitbox.fill((r, 255, 0))
                    self.super_brain[locs[i]]["hitbox"]= hitbox
                else:
                    self.super_brain[locs[i]]["hitbox"].fill((r, 255, 0))
            self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]
                

    def reinforced_pathfinding(self, executions= 50, initial_explo_rate= 0.4):
        life_penalty= 0
        #life_penalty= 1/executions
        explo_rate= initial_explo_rate
        exec= executions
        locations= [agent.INIT_POSITION for agent in self.agents]
        angles= [0 for agent in self.agents]
        self.env.show_agents_updates(self.agents, locations, angles)
        for i, agent in enumerate(self.agents):
            if locations[i] not in agent.brain.keys():
                agent.brain[locations[i]]= {"rewards": agent.get_state_reward(locations[i], angles[i], life_penalty), "angle":0, "previous_state": None, "action": -1}
            if locations[i] not in self.super_brain.keys():
                self.super_brain[locations[i]]= {"rewards": agent.get_state_reward(locations[i], angles[i], life_penalty)}
        isStarted= False
        visited_states= [[loc] for loc in locations]
        previous_states= [loc for loc in locations]
        rewards= [0 for agent in self.agents]
        needReset= [False for agent in self.agents]
        while executions >= 0:
            explo_rate= explo_rate * (1 - (1/exec))
            game_over= [False for agent in self.agents]
            scores= [0 for agent in self.agents]
            if not isStarted:
                visited_states= [[loc] for loc in locations]
                isStarted= True
            actions= [self.select_opti_action(loc, angles[i], self.agents[i], initial_explo_rate) if game_over[i] == False else actions[i] for i, loc in enumerate(locations)]
            for i, agent in enumerate(self.agents):
                if game_over[i] == False:
                    #locations[i], angles[i]= agent.simulated_take_action(locations[i], angles[i], actions[i])
                    l, an= agent.simulated_take_action(locations[i], angles[i], actions[i])
                    tries= 3
                    a=0
                    while l in visited_states[i]:
                        a= self.select_opti_action(locations[i], angles[i], agent)
                        l, an= agent.simulated_take_action(locations[i], angles[i], a)
                        tries-= 1
                        if tries == 0:
                            break
                    previous_states[i]= locations[i]
                    locations[i]= l
                    angles[i]= an
                    if tries < 3:
                        actions[i]= a
                    visited_states[i].append(locations[i])
                    if locations[i] not in self.super_brain.keys():
                        self.super_brain[locations[i]]= {"rewards": agent.get_state_reward(locations[i], angles[i], life_penalty)}
                    if locations[i] not in agent.brain.keys():
                        agent.brain[locations[i]]= {"rewards": agent.get_state_reward(locations[i], angles[i], life_penalty), "angle": angles[i], "previous_state": previous_states[i], "action": actions[i]}
                    else:
                        agent.brain[locations[i]]["action"]= actions[i]
                        agent.brain[locations[i]]["previous_state"]= previous_states[i]   
                        agent.brain[locations[i]]["angle"]= angles[i]
            rewards= [self.agents[i].get_environment_feedback(locations[i], angles[i]) for i in range(len(locations))]
            game_over= [1 if reward == -1 or reward == 1 else 0 for reward in rewards]
            self.env.show_agents_updates(self.agents, locations, angles)
            for i in range(len(scores)):
                scores[i]+= rewards[i]

            if np.sum(game_over) == len(game_over):
            #if 1 in rewards or -1 in rewards:               #Cycle terminé | Mise à jour des récompenses(via retrospective du chemin parcouru)
                for i in range(len(rewards)):
                    if rewards[i] != 0:
                        self.agents[i].brain[locations[i]]["rewards"]= [rewards[i] for _ in range(3)]
                        self.super_brain[locations[i]]["rewards"]= [rewards[i] for _ in range(3)]
                        if rewards[i] == -1:
                            if "hitbox" not in self.super_brain[locations[i]].keys():
                                hitbox= pygame.Surface((PLAYER_WIDTH, PLAYER_WIDTH), pygame.SRCALPHA)
                                hitbox.fill((255, 0, 0))
                                self.super_brain[locations[i]]["hitbox"]= hitbox
                        else:
                            print("SUCCESS")
                next_states= [loc for loc in locations]
                locs= [previous_state for previous_state in previous_states]
                actions= [agent.brain[loc]["action"] for loc, agent in zip(locs, self.agents)]
                angles= [agent.brain[loc]["angle"] for loc, agent in zip(locs, self.agents)]
                rewards= [self.agents[i].get_environment_feedback(locs[i], angles[i]) for i in range(len(locs))]
                self.update_brain(next_states, locs, rewards, actions, needReset)
                for i, agent in enumerate(self.agents):
                    if agent.brain[locs[i]]["previous_state"] == None:
                        needReset[i]= True
                if np.sum(needReset) == len(needReset):
                    isStarted= False
                    locations= [agent.INIT_POSITION for agent in self.agents]
                    angles= [0 for agent in self.agents]
                    executions-= 1
                    self.env.show_agents_updates(self.agents, locations, angles)
                    self.env.show_super_brain_updates(self.super_brain)
                    print("--> FIN DE L'APPRENTISSAGE <--")
                    print("Nombre d'exécutions restantes= ", executions)
                    print("Scores= ", scores)
                    needReset= [False for agent in self.agents]
                    time.sleep(1)
                else:
                    while True:
                        next_states= [loc for loc in locs] 
                        locs= [(0, 0) for next_states in next_states]
                        actions= [0 for next_states in next_states]
                        rewards= [0 for next_states in next_states]
                        angles= [0 for next_states in next_states]
                        for i in range(len(next_states)):
                            if needReset[i] == False:
                                if self.agents[i].brain[next_states[i]]["previous_state"] == None:
                                    needReset[i]= True
                                else:
                                    locs[i]= self.agents[i].brain[next_states[i]]["previous_state"]
                                    actions[i]= self.agents[i].brain[locs[i]]["action"]
                                    angles[i]= self.agents[i].brain[locs[i]]["angle"]
                                    rewards[i]= self.agents[i].get_environment_feedback(locs[i], angles[i])
                        self.update_brain(next_states, locs, rewards, actions, needReset)
                        if np.all(needReset):
                            isStarted= False
                            locations= [agent.INIT_POSITION for agent in self.agents]
                            angles= [0 for agent in self.agents]
                            executions-= 1
                            self.env.show_agents_updates(self.agents, locations, angles)
                            self.env.show_super_brain_updates(self.super_brain)
                            print("--> FIN DE L'APPRENTISSAGE <--")
                            print("Nombre d'exécutions restantes= ", executions)
                            print("Scores= ", scores)
                            needReset= [False for agent in self.agents]
                            time.sleep(1)
                            break
        final_position= self.agents[0].INIT_POSITION
        final_angle= 0
        optimal_strategy= []
        print("Optimal strategy= ", optimal_strategy)
        return optimal_strategy
        
                