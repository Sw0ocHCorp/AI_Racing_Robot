import pygame
from pygame.sprite import *
from PIL import Image

rob_pb= Image.open("Software_Game_Assets/sendRobot_pushButton.png")
exp_pb= Image.open("Software_Game_Assets/sendRobot_pushButton.png")
txt_entry= Image.open("Software_Game_Assets/text_entry.png")


class MenuWidget:
    def __init__(self, window):
        pygame.font.init()
        self.font= pygame.font.Font("Software_Game_Assets/PressStart2P-vaV7.ttf", 10)
        self.menu_sprites= Group()
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

    def robot_pb_interaction(self, mouse_position):
        if self.robot_pb_rect.collidepoint(mouse_position):
            print("Send Strategy to Robot")
            return True
        else:
            return False
    
    def experiment_pb_interaction(self, mouse_position):
        if self.experiment_pb_rect.collidepoint(mouse_position):
            print("Experiment Launched")
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
        

