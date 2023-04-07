import pygame
from pygame.sprite import Sprite
from PIL import Image
import numpy as np
import math


DROITE= 0
GAUCHE= 1
AVANT= 2

PLAYER_CAR= pygame.image.load("Software_Game_Assets\Player_car_final.png")
player_img= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
HEIGHT= 900
WIDTH= 1500
WIDTH_ENV= 800
WINDOW= pygame.display.set_mode((WIDTH, HEIGHT))

class ReinforcementAgent(pygame.sprite.Sprite):
    def __init__(self, environment, velocity, rotation_angle, skin= "Software_Game_Assets\Player_car_final.png", position= (round((WIDTH_ENV/2) - (PLAYER_WIDTH / 2), 4), round(HEIGHT - (PLAYER_HEIGHT/1.7), 4))):
        super().__init__()
        self.SKIN= pygame.image.load(skin)
        self.image= self.SKIN
        self.velocity= velocity
        self.rotation_angle= rotation_angle
        self.angle= 0
        self.INIT_POSITION= position
        self.rect= self.image.get_rect()
        self.rect.center= self.INIT_POSITION
        self.strategy= np.array([])
        self.simulation_angle= 0
        self.simulation_position= self.INIT_POSITION
        self.env= environment
        self.brain= {}
    
    #Fonction de Mouvement de l'Agent
    def set_state(self, position, angle):
        self.position= position
        self.rect.center= position
        self.angle= angle
        self.image= pygame.transform.rotate(self.SKIN, angle)
        self.rect= self.image.get_rect(center= self.position)
    
    def rotate(self, isLeft):
        if isLeft:
            self.angle+= self.rotation_angle
        else:
            self.angle-= self.rotation_angle
        if self.angle > 360:
            self.angle-= 360
        self.image= pygame.transform.rotate(self.SKIN, self.angle)
        self.rect= self.image.get_rect(center= self.rect.center)
    
    def simulated_rotation(self, isLeft, angle= 0):
        if isLeft:
            angle+= self.rotation_angle
        else:
            angle-= self.rotation_angle
        if angle> 360:
            angle-= 360
        return angle

    def movement(self):
        radian_angle= math.radians(self.angle)
        self.rect.centerx -= self.velocity * math.sin(radian_angle)
        self.rect.centery -= self.velocity * math.cos(radian_angle)
    
    def simulated_movement(self, position, angle):
        radian_angle= math.radians(angle)
        location= list(position)
        location[0] -= round(self.velocity * math.sin(radian_angle), 4)
        location[1] -= round(self.velocity * math.cos(radian_angle), 4)
        location= tuple(location)
        return location
    
    def select_action(self, action):
        if action == DROITE:
            self.rotate(False)
            self.movement()
        elif action == GAUCHE:
            self.rotate(True)
            self.movement()
        elif action == AVANT:
            self.movement()
        np.append(self.strategy, action)
    
    def simulated_take_action(self, position, angle, action):
        update_angle= 0
        update_location= (0,0)
        if action == DROITE:
            update_angle= self.simulated_rotation(False, angle)
            update_location= self.simulated_movement(position, update_angle)
        elif action == GAUCHE:
            update_angle= self.simulated_rotation(True, angle)
            update_location= self.simulated_movement(position, update_angle)
        elif action == AVANT:
            update_location= self.simulated_movement(position, angle)
        np.append(self.strategy, action)
        return update_location , update_angle
    
    def get_environment_feedback(self, location, angle):
        assert self.image != None
        ghost_agent= Sprite()
        ghost_agent.rect= self.image.get_rect(center= location)
        ghost_agent.image= pygame.transform.rotate(self.SKIN, angle)
        ghost_agent.rect= ghost_agent.image.get_rect(center= ghost_agent.rect.center)
        collided_sprites= pygame.sprite.spritecollide(ghost_agent, self.env.STATIC_SPRITES, False)
        if self.env.FINISH_LINE in collided_sprites:
            return 1
        elif self.env.FINISH_LINE not in collided_sprites and len(collided_sprites) > 0 or (ghost_agent.rect.top > 900 or ghost_agent.rect.bottom > 900):
            return -1
        else:
            return 0

    def reset_state(self):
        self.rect.center= self.INIT_POSITION
        self.strategy= np.array([])
        self.angle= 0
        self.image= self.SKIN
        self.rect= self.image.get_rect(center= self.INIT_POSITION)
    



class QLearningAlgorithm():
    def __init__(self, environment, nb_agents= 1):
        self.super_brain= {}
        self.env= environment
        self.agents= []
        for i in range(nb_agents):
            self.agents.append(ReinforcementAgent(self.env, velocity= 20, rotation_angle= 45))
        
    def select_opti_action(self, position, exploration_rate= 0.25):
        rewards= self.super_brain[position]["rewards"]
        if np.random.rand() < exploration_rate or np.max(rewards) == 0:
            return np.random.randint(0, 3)
        else:
            return np.argmax(rewards)
    
    def update_brain(self, next_locs, locs, rewards, actions, alpha= 0.25, gamma= 0.9):
        conflict_indexs= []
        corrects_indexs= []
        garbage_indexs= []
        correct_pos= []
        for i, l in enumerate(locs):
            if l == (-1, -1):
                garbage_indexs.append(i)
            elif l not in correct_pos:
                correct_pos.append(l)
                corrects_indexs.append(i)
            else:
                conflict_indexs.append(i)
        updated_rewards= np.zeros(len(locs))
        for i, loc in enumerate(locs):
            if i not in garbage_indexs:
                if rewards[i] == -1:
                    updated_rewards[i]= rewards[i]
                    self.agents[i].brain[loc]["rewards"][actions[i]]= rewards[i]
                else:
                    future_rewards= self.agents[i].brain[next_locs[i]]["rewards"]
                    updated_rewards[i]= ((1-alpha) * self.super_brain[loc]["rewards"][actions[i]]) + alpha*(rewards[i] + gamma * np.max(future_rewards))
                    self.agents[i].brain[loc]["rewards"][actions[i]]= rewards[i]
        for i in conflict_indexs:
            if updated_rewards[i] == -1:
                self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]
            if updated_rewards[i] > self.super_brain[locs[i]]["rewards"][actions[i]]:
                self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]
        for i in corrects_indexs:
            if updated_rewards[i] == -1:
                self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]
            if updated_rewards[i] > self.super_brain[locs[i]]["rewards"][actions[i]]:
                self.super_brain[locs[i]]["rewards"][actions[i]]= updated_rewards[i]

    def reinforced_pathfinding(self):
        locations= [agent.INIT_POSITION for agent in self.agents]
        angles= [0 for agent in self.agents]
        self.env.show_agents_updates(self.agents, locations, angles)
        for i, agent in enumerate(self.agents):
            if locations[i] not in agent.brain.keys():
                agent.brain[locations[i]]= {"rewards": [0, 0, 0], "previous_state": None, "action": -1}
            if locations[i] not in self.super_brain.keys():
                self.super_brain[locations[i]]= {"rewards": [0, 0, 0]}
        isStarted= False
        executions= 500
        visited_states= [[loc] for loc in locations]
        previous_states= [loc for loc in locations]
        rewards= [0 for agent in self.agents]
        needReset= [False for agent in self.agents]
        while executions >= 0:
            scores= [0 for agent in self.agents]
            if not isStarted:
                visited_states= [[loc] for loc in locations]
                isStarted= True
            actions= [self.select_opti_action(loc) for loc in locations]
            for i, agent in enumerate(self.agents):
                agent.brain[locations[i]]["action"]= actions[i]
                previous_states[i]= locations[i]
                locations[i], angles[i]= agent.simulated_take_action(locations[i], angles[i], actions[i])
                while locations[i] in visited_states[i]:
                    actions[i]= self.select_opti_action(locations[i])
                    locations[i], angles[i]= agent.simulated_take_action(locations[i], angles[i], actions[i])
                visited_states[i].append(locations[i])
                if locations[i] not in self.super_brain.keys():
                    self.super_brain[locations[i]]= {"rewards": [0, 0, 0]}
                if locations[i] not in agent.brain.keys():
                    agent.brain[locations[i]]= {"rewards": [0, 0, 0], "previous_state": previous_states[i], "action": actions[i]}
                else:
                    agent.brain[locations[i]]["action"]= actions[i]
                    agent.brain[locations[i]]["previous_state"]= previous_states[i]   
            rewards= [self.agents[i].get_environment_feedback(locations[i], angles[i]) for i in range(len(locations))]
            self.env.show_agents_updates(self.agents, locations, angles)
            for i in range(len(scores)):
                scores[i]+= rewards[i]
            if 1 in rewards or -1 in rewards:               #Cycle terminé | Mise à jour des récompenses(via retrospective du chemin parcouru)
                for i in range(len(rewards)):
                    if rewards[i] == -1 or rewards[i] == 1:
                        self.agents[i].brain[locations[i]]["rewards"]= [rewards[i] for _ in range(3)]
                        self.super_brain[locations[i]]["rewards"]= [rewards[i] for _ in range(3)]
                next_states= [loc for loc in locations]
                locs= [previous_state for previous_state in previous_states]
                actions= [agent.brain[loc]["action"] for loc, agent in zip(locs, self.agents)]
                self.update_brain(next_states, locs, rewards, actions)
                for i, agent in enumerate(self.agents):
                    if agent.brain[locs[i]]["previous_state"] == None:
                        needReset[i]= True
                        locs[i]= (-1, -1)
                if np.sum(needReset) == len(needReset):
                    isStarted= False
                    locations= [agent.INIT_POSITION for agent in self.agents]
                    executions-= 1
                    angles= [0 for agent in self.agents]
                    self.env.show_agents_updates(self.agents, locations, angles)
                    print("--> FIN DE L'APPRENTISSAGE <--")
                    print("Nombre d'exécutions restantes= ", executions)
                    print("Scores= ", scores)
                else:
                    while True:
                        next_states= [loc for loc in locs] 
                        locs= []
                        actions= []
                        rewards= []
                        
                        for i, next_loc in enumerate(next_states):
                            if self.agents[i].brain[next_loc]["previous_state"] == None:
                                needReset[i]= True
                                locs.append((-1, -1))
                                actions.append(-1)
                            else:
                                if next_loc != (-1, -1):
                                    locs.append(self.agents[i].brain[next_loc]["previous_state"])
                                else:
                                    locs.append((-1, -1))
                                if locs[i] != (-1, -1):
                                    actions.append(self.agents[i].brain[locs[i]]["action"])
                                else:
                                    actions.append(-1)
                                if locs[i] != (-1, -1):
                                    rewards.append(self.agents[i].get_environment_feedback(locs[i], angles[i]))
                                else:
                                    rewards.append(-667)
                        self.update_brain(next_states, locs, rewards, actions)
                        if np.all(needReset):
                            isStarted= False
                            locations= [agent.INIT_POSITION for agent in self.agents]
                            angles= [0 for agent in self.agents]
                            executions-= 1
                            self.env.show_agents_updates(self.agents, locations, angles)
                            print("--> FIN DE L'APPRENTISSAGE <--")
                            print("Nombre d'exécutions restantes= ", executions)
                            print("Scores= ", scores)
                            break
                
        strategies= []
        for agent in self.agents:
            strategies.append(agent.strategy)
        return strategies
        
                