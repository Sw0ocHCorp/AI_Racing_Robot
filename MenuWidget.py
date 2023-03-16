import pygame
from pygame.sprite import *
from PIL import Image
import numpy as np
from Agent import Agent
from MCTreeSearch import *

rob_pb= Image.open("Software_Game_Assets/sendRobot_pushButton.png")
exp_pb= Image.open("Software_Game_Assets/sendRobot_pushButton.png")
txt_entry= Image.open("Software_Game_Assets/text_entry.png")
agents_img= pygame.image.load("Software_Game_Assets/car1.png")
agents_width= agents_img.get_rect().width
agents_height= agents_img.get_rect().height
agents_img= pygame.transform.scale(agents_img, (int(agents_width/2), int(agents_height/2)))

best_agents_img= pygame.image.load("Software_Game_Assets/Player_car_final.png")
best_agents_width= best_agents_img.get_rect().width
best_agents_height= best_agents_img.get_rect().height
best_agents_img= pygame.transform.scale(best_agents_img, (int(best_agents_width/2), int(best_agents_height/2)))

opti_img= pygame.image.load("Software_Game_Assets/arrow_optimization.png")
opti_width= opti_img.get_rect().width
opti_height= opti_img.get_rect().height
opti_img= pygame.transform.scale(opti_img, (int(opti_width/25), int(opti_height/25)))
opti_img= pygame.transform.rotate(opti_img, 180)
pygame.font.init()
SCORE_FONT= pygame.font.Font("Software_Game_Assets/PressStart2P-vaV7.ttf", 7)
TREE_WIDTH= 1480 - 820
WIDTH_ENV= 820


class MenuWidget:
    def __init__(self, window):
        pygame.font.init()
        self.font= pygame.font.Font("Software_Game_Assets/PressStart2P-vaV7.ttf", 10)
        self.width_opti_img= np.zeros(10)
        self.init_fit_dict= dict()
        self.new_fit_dict= []
        self.menu_sprites= Group()
        self.mcts_menu_sprites= Group()
        self.init_agents= Group()
        self.new_agents= Group()
        self.opti_sprites= Group()
        self.experiment_pb= Sprite()
        self.experiment_pb.image= pygame.image.load("Software_Game_Assets/runExp_pushButton.png")
        self.robot_pb= Sprite()
        self.robot_pb.image= pygame.image.load("Software_Game_Assets/sendRobot_pushButton.png")
        self.pop_entry= Sprite()
        self.pop_entry.image= pygame.image.load("Software_Game_Assets/text_entry.png")
        self.nfe_entry= Sprite()
        self.nfe_entry.image= pygame.image.load("Software_Game_Assets/text_entry.png")
        self.window= window
        self.menu_sprites.add(self.experiment_pb, self.robot_pb, self.pop_entry, self.nfe_entry)
        self.mcts_menu_sprites.add(self.experiment_pb, self.robot_pb)
        width_window= self.window.get_width()
        height_window= self.window.get_height()
        self.robot_pb.rect= self.robot_pb.image.get_rect()
        self.robot_pb.rect.center= (width_window- int(rob_pb.width/2 + 10), height_window- int(rob_pb.height/2 + 10))
        self.pop_entry.rect= self.pop_entry.image.get_rect()
        self.pop_entry.rect.center= (int(txt_entry.width/2) + 10, height_window- (int(exp_pb.height)*1.5 + 10))
        self.nfe_entry.rect= self.nfe_entry.image.get_rect()
        self.nfe_entry.rect.center= (int(self.pop_entry.rect.topright[0] + exp_pb.width/2)+ 10, height_window- (int(exp_pb.height)*1.5 + 10))
        self.experiment_pb.rect= self.experiment_pb.image.get_rect()
        self.experiment_pb.rect.center= (int(self.pop_entry.rect.right)+ 5, height_window- (int(exp_pb.height/2) + 10))
        self.pop_entry_rect= self.pop_entry.rect
        self.robot_pb_rect= self.robot_pb.rect
        self.experiment_pb_rect= self.experiment_pb.rect
        self.nfe_entry_rect= self.nfe_entry.rect
        self.pop_buffer= ""
        self.nfe_buffer= ""
        self.last_height= 0

    def attach_mcts_algo(self, mcts_algo):
        self.mcts_algo= mcts_algo

    def draw_menu(self):
        self.menu_sprites.draw(self.window)
        pop_buffer= self.font.render(self.pop_buffer, True, "black")
        self.window.blit(pop_buffer, (self.pop_entry_rect.left+10, self.pop_entry_rect.centery-5))
        nfe_buffer= self.font.render(self.nfe_buffer, True, "black")
        self.window.blit(nfe_buffer, (self.nfe_entry_rect.left+10, self.nfe_entry_rect.centery-5))
        pop_title= [self.font.render("Population", True, "black"), self.font.render("Size", True, "black")]
        nfe_title= [self.font.render("Max", True, "black"), self.font.render("NFE", True, "black")]
        self.window.blit(pop_title[0], (self.pop_entry_rect.left, self.pop_entry_rect.top-24))
        self.window.blit(pop_title[1], (self.pop_entry_rect.left, self.pop_entry_rect.top-12))
        self.window.blit(nfe_title[0], (self.nfe_entry_rect.left+10, self.nfe_entry_rect.top-24))
        self.window.blit(nfe_title[1], (self.nfe_entry_rect.left+10, self.nfe_entry_rect.top-12))
    
    def draw_mcts_menu(self):
        self.mcts_menu_sprites.draw(self.window)
        #self.show_tree()
        """pop_buffer= self.font.render(self.pop_buffer, True, "black")
        self.window.blit(pop_buffer, (self.pop_entry_rect.left+10, self.pop_entry_rect.centery-5))
        nfe_buffer= self.font.render(self.nfe_buffer, True, "black")
        self.window.blit(nfe_buffer, (self.nfe_entry_rect.left+10, self.nfe_entry_rect.centery-5))
        pop_title= [self.font.render("Population", True, "black"), self.font.render("Size", True, "black")]
        nfe_title= [self.font.render("Max", True, "black"), self.font.render("NFE", True, "black")]"""

        
    def set_init_fitness(self, fitness):
        j= 0
        reset_x_loc= False
        sorted_fitness= sorted(fitness, reverse= True)
        for i, f in enumerate(sorted_fitness):
            if i == 0:
                best_agent= Sprite()
                best_agent.image= best_agents_img
                best_agent.rect= best_agent.image.get_rect()
                best_agent.rect.center= (800 + agents_width, 50)
                self.width_opti_img[i]= 800 + agents_width
                self.init_agents.add(best_agent)
                fitness_buffer= SCORE_FONT.render(str(f), True, "black")
                self.init_fit_dict[i]= (fitness_buffer, best_agent.rect.left, best_agent.rect.bottom + 5)
            else:
                self.width_opti_img[i]= 800 + agents_width + int(agents_width + 15)*i+1
                agent= Sprite()
                agent.image= agents_img
                agent.rect= agent.image.get_rect()
                if i % 10 == 0:
                    j+=1
                    reset_x_loc= True
                if reset_x_loc:
                    agent.rect.center= (800 + agents_width + int(agents_width + 15)*(i-j*10), 50 + agents_height*j)
                else:
                    agent.rect.center= (800 + agents_width + int(agents_width + 15)*i+1, 50 + agents_height*j)
                fitness_buffer= SCORE_FONT.render(str(f), True, "black")
                self.init_fit_dict[i]= (fitness_buffer, agent.rect.left, agent.rect.bottom + 5)
                self.last_height= agent.rect.bottom + 15 
                self.init_agents.add(agent)
        sprite= Sprite()
        sprite.image= opti_img
        sprite.rect= sprite.image.get_rect()
        sprite.rect.center= (800 + ((self.window.get_width() - 800)/2), self.last_height + 40)
        self.last_height= sprite.rect.bottom + 5
        self.opti_sprites.add(sprite)

    def show_init_agents(self):
        if len(self.init_agents.spritedict) > 0:
            self.init_agents.draw(self.window)
            self.opti_sprites.draw(self.window)
            for i in self.init_fit_dict:
                self.window.blit(self.init_fit_dict[i][0], (self.init_fit_dict[i][1], self.init_fit_dict[i][2]))
    
    def set_new_fitness(self, new_fitness):
        sorted_fitness= sorted(new_fitness, reverse= True)
        j=0
        reset_x_loc= False
        last_height= self.last_height
        for i, f in enumerate(sorted_fitness):
            if i == 0:
                best_agent= Sprite()
                best_agent.image= best_agents_img
                best_agent.rect= best_agent.image.get_rect()
                best_agent.rect.center= (800 + agents_width, last_height + 20)
                self.new_agents.add(best_agent)
                fitness_buffer= SCORE_FONT.render(str(f), True, "black")
                self.new_fit_dict.append((fitness_buffer, best_agent.rect.left, best_agent.rect.bottom + 5))
            else:
                agent= Sprite()
                agent.image= agents_img
                agent.rect= agent.image.get_rect()
                if i % 10 == 0:
                    j+=1
                    reset_x_loc= True
                if reset_x_loc:
                    agent.rect.center= (800 + agents_width + int(agents_width + 15)*(i-j*10), last_height + 20 + agents_height*j)
                else:
                    agent.rect.center= (800 + agents_width + int(agents_width + 15)*i, last_height +  20 + agents_height*j)
                fitness_buffer= SCORE_FONT.render(str(f), True, "black")
                self.new_fit_dict.append((fitness_buffer, agent.rect.left, agent.rect.bottom + 5))
                self.last_height= agent.rect.bottom + 15 
                self.new_agents.add(agent)
        sprite= Sprite()
        sprite.image= opti_img
        sprite.rect= sprite.image.get_rect()
        sprite.rect.center= (800 + ((self.window.get_width() - 800)/2), self.last_height + 40)
        self.last_height= sprite.rect.bottom + 5
        self.opti_sprites.add(sprite)
        
    def show_new_agents(self, isOptiAfter= True):
        if len(self.new_agents.spritedict) > 0:
            self.new_agents.draw(self.window)
            if isOptiAfter:
                self.opti_sprites.draw(self.window)
            for i in range(len(self.new_fit_dict)):
                self.window.blit(self.new_fit_dict[i][0], (self.new_fit_dict[i][1], self.new_fit_dict[i][2]))

    def show_tree(self):
        for state in self.mcts_algo.ui_states:
            state.draw_state(self.window)


    def robot_pb_interaction(self, mouse_position):
        if self.robot_pb_rect.collidepoint(mouse_position):
            print("Send Strategy to Robot")
            return True
        else:
            return False
    
    def experiment_pb_interaction(self, mouse_position):
        if self.experiment_pb_rect.collidepoint(mouse_position):
            print("Experiment Launched")
            if self.pop_buffer != "":
                self.width_opti_img= np.zeros(int(self.pop_buffer))
            return True
        else:
            return False
        
    
    def pop_entry_interaction(self, mouse_position):
        if self.pop_entry_rect.collidepoint(mouse_position):
            print("Pop Entry")
            return True
        else:
            return False
    
    def nfe_entry_interaction(self, mouse_position):
        if self.nfe_entry_rect.collidepoint(mouse_position):
            print("NFE Entry")
            return True
        else:
            return False
    
    def pop_write_text(self, text):
        self.pop_buffer+= text
        pop_buffer= self.font.render(self.pop_buffer, True, "black")
        print(self.pop_buffer)
        self.window.blit(pop_buffer, (self.pop_entry_rect.left+10, self.pop_entry_rect.centery-5))
        
    def pop_backspace(self):
        self.pop_buffer= self.pop_buffer[:-1]
        pop_buffer= self.font.render(self.pop_buffer, True, "black")
        print(self.pop_buffer)
        self.window.blit(pop_buffer, (self.pop_entry_rect.left+10, self.pop_entry_rect.centery-5))
    
    def nfe_write_text(self, text):
        self.nfe_buffer+= text
        nfe_buffer= self.font.render(self.nfe_buffer, True, "black")
        print(self.nfe_buffer)
        self.window.blit(nfe_buffer, (self.nfe_entry_rect.left+10, self.nfe_entry_rect.centery-5))

    def nfe_backspace(self):
        self.nfe_buffer= self.nfe_buffer[:-1]
        nfe_buffer= self.font.render(self.nfe_buffer, True, "black")
        print(self.nfe_buffer)
        self.window.blit(nfe_buffer, (self.nfe_entry_rect.left+10, self.nfe_entry_rect.centery-5))
    
    def clear_text(self):
        self.nfe_buffer= ""
        self.pop_buffer= ""
        self.menu_sprites.draw(self.window)
        

