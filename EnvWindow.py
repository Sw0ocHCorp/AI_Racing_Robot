import pygame
import tkinter as tk
from tkinter import font
import os
import platform
from itertools import cycle
import traceback


class Game:
    def __init__(self, root):
        self.root = root
        embed = tk.Frame(root,
                         width=600,
                         height=600)
        embed.pack(side=tk.TOP)
        
        # some SDL magic (don't know how and why this works tbh)
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        # itialize a pygame display
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        self.screen.fill(pygame.Color('red'))
        self.clock = pygame.time.Clock()
        
        # --------------------------------------------------------------
        # everything from here is optional and only for demonstration

        # create a cycle of colors to have something that animates
        self.timer = 0
        self.colors = cycle(['red', 'yellow', 'green', 'turquoise', 
                             'blue', 'purple'])
        # different delay times in second that one can iterate over
        self.delays = cycle([1, 0.5, 0.1])
        self.color = next(self.colors)
        self.delay = next(self.delays)
        
        # create a tk Button that changes the animation speed
        helv = font.Font(family='Helvetica', size=18, weight='bold')
        self.button = tk.Button(root, 
                                text="Change speed",
                                font=helv,
                                command=self.change_speed).pack(side=tk.BOTTOM)
        # ---------------------------------------------------------------
    
    def change_speed(self):
        # change the animation delay
        self.delay = next(self.delays)
        
    def run(self):
        # Pygame loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.timer += self.clock.tick(60) / 1000

            # --- also optional ----------------------------
            # change the screen color after the given delay
            if self.timer >= self.delay:
                self.color = next(self.colors)
                self.timer = 0
            self.screen.fill(pygame.Color(self.color))    
            # ----------------------------------------------

            pygame.display.update()
            
            # update the tkinter root (I need this try except for some reason,
            # otherwise I get an error when closing the window)
            try:
                self.root.update()
            except tk.TclError:
                running = False   
        pygame.quit()

try:
    # initialise the root widget
    root = tk.Tk()
    root.geometry('600x660')
    # initialise and run the game
    game = Game(root)
    game.run()
except Exception:
    traceback.print_exc()
    pygame.quit()