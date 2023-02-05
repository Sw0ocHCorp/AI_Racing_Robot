from Agent import Agent
import numpy as np
import random

class PopulationEA:
    def __init__(self, elements= np.array([], dtype= Agent)):
        self.saved_elements= elements
        POP_SIZE= len(elements)
        self.fitness= np.zeros(POP_SIZE)
        self.elements= elements
        self.table_transition= dict()
    
    def evaluate_element(self, element):
        pass

    def crossover(self):
        pass
        """self.selected_parents= random.choices(self.elements, k= 5)
        best_parent= np.argmax(self)"""

    def mutation(self):
        pass

    def remplacement(self):
        pass

    