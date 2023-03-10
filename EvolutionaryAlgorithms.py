from pygame.sprite import *
import random
import numpy as np
from PIL import Image
from threading import Thread
from MenuWidget import MenuWidget
from Agent import Agent

# --> Genetic Algorithm <-- #
HEIGHT= 900
WIDTH= 800
player_img= Image.open("Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
class GeneticAlgorithm():
    def __init__(self, agents, evaluate, isThreadEvaluation= False):
        print("Generation #0")
        print("-----------------------------")
        self.isThreadEvaluation= isThreadEvaluation
        self.agents= agents
        self.population = np.array([agent.strategy for agent in self.agents])
        self.l= self.population.shape[1]
        self.evaluate= evaluate
        if self.isThreadEvaluation:
            self.fitness= evaluate(self.agents)
        else:
            self.fitness = np.array(self.evaluate(self.agents))
        self.isFinished= False
        self.max_nfe= 1000

    def set_max_nfe(self, max_nfe):
        self.max_nfe= max_nfe
    
    def begin_menu_connection(self, menu):
        self.menu= menu
        self.menu.set_init_fitness(self.fitness)

    def selection(self, t=2):
        #Implémenter le Tournament selection
        selected_indexs= random.sample(range(len(self.fitness)), t)
        selected_individual = np.argmax([self.fitness[i] for i in selected_indexs])
        return self.population[selected_individual]
        
    def crossover(self, parent1, parent2):
        #Appeler la Tournament Selection 
        min_lenght= min(len(parent1), len(parent2))
        mid_len= int(min_lenght/2)
        brkpt1= random.randint(1, mid_len)
        brkpt2= random.randint(mid_len, min_lenght-1)

        child1= np.concatenate((parent1[:brkpt1], parent2[brkpt1:brkpt2], parent1[brkpt2:]), axis= None)           # parent_1 -> | breakpoint | parent_2 ->
        child2= np.concatenate((parent2[:brkpt1], parent1[brkpt1:brkpt2], parent2[brkpt2:]), axis= None)            # parent_2 -> | breakpoint | parent_1 ->
        #Effectuer le crossover des parents sélectionnés
        return [child1, child2]

    def mutation(self, individual, p=0.1):
        #Implémenter une méthode de mutation
        for index_flip in range(len(individual)):
            if random.random() < p:
                individual[index_flip]= abs(1-individual[index_flip])
        return individual

    def create_offspring(self, parents_strategies, t=2):
        offspring= np.empty((0, self.l))
        for i in range(len(parents_strategies)):
            parent1= self.selection(t)
            parent2= self.selection(t)
            childs= self.crossover(parent1, parent2)
            childs= np.array([self.mutation(child) for child in childs])
            offspring= np.concatenate((offspring, childs), axis= 0)
        return offspring

    def replacement(self, parents_strategies, offspring_strategies, k= 1):
        parents_strategies= parents_strategies.astype(int)
        offspring_strategies= offspring_strategies.astype(int)
        new_generation= np.empty((0, parents_strategies.shape[1]))
        new_fitness= np.array([])
        pop_size= len(parents_strategies)
        #Evaluer la nouvelle population(Offspring)
        offspring_agents= [off_agent for off_agent in self.distribute_strategies(offspring_strategies)]
        if self.isThreadEvaluation:
            fitness_offspring= self.evaluate(offspring_agents)
        else:
            fitness_offspring= np.array([self.evaluate(agent) for agent in offspring_agents])
        #Elitisme --> garder les K meilleurs individus de la Génération précédente
        best_index= np.argmax(self.fitness)
        if self.fitness[best_index] > 0:
            while k > 0:
                k-= 1
                best_index= np.argmax(self.fitness)
                if self.fitness[best_index] > 0:
                    new_generation= np.vstack((new_generation, self.population[best_index]))
                    new_fitness= np.append(new_fitness, self.fitness[best_index])
                    self.fitness= np.delete(self.fitness, best_index)
        new_generation= np.concatenate((new_generation, offspring_strategies[:pop_size-len(new_generation)]), axis= 0)
        new_fitness= np.concatenate((new_fitness, fitness_offspring[:pop_size-len(new_fitness)]), axis= None)
        self.population= np.array(new_generation)
        self.agents= [new_agent for new_agent in self.distribute_strategies(self.population)]
        self.menu.set_new_fitness(new_fitness)
        self.fitness= np.array(new_fitness)
        #Remplir le reste population avec les individus de la nouvelle population

    def start_optimization(self):
        num_gen= 1
        nfe= 0
        nfe += len(self.population)
        while nfe < self.max_nfe:
            print("-----------------------------")
            print("==> Generation #" + str(num_gen))
            print("-----------------------------")
            offspring= self.create_offspring(self.population)
            nfe += len(offspring)
            self.replacement(self.population, offspring, k= int(self.population.shape[0]//2))
            num_gen += 1
        best_index= np.argmax(self.fitness)
        self.isFinished= True
        self.menu.show_new_agents(isOptiAfter= False)
        return self.population[best_index], self.fitness[best_index]
    
    def distribute_strategies(self, strategies):
        agents_created= None
        agents_created= np.array([Agent(velocity= 10, rotation_angle= 45, 
                                    position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                    skin= "Software_Game_Assets/car1.png") for i in range(strategies.shape[0])], dtype= Agent)
        for i in range(len(agents_created)):
            agents_created[i].strategy= strategies[i]
        return agents_created

# --> Differential Evolution Algorithm <-- #
class DifferentialEvolution:
    def __init__(self, agents, evaluate):
        self.agents= agents
        self.population = np.array([agent.strategy for agent in self.agents])
        self.l= self.population.shape[1]
        self.evaluate= evaluate
        self.fitness = np.array([self.evaluate(individual) for individual in self.population])
    
    def mutation(self, population, target_individual, F= 0.5):
        pop= population.copy()
        pop= np.delete(pop, target_individual, axis= 0)
        selected_individuals=random.sample(list(pop), 3)
        mutated_individual= np.round_(np.clip(selected_individuals[0] + F*(selected_individuals[1] - selected_individuals[2]), 0, 1))
        mutated_individual= mutated_individual.astype(int)
        return mutated_individual

    def crossover_selection(self, target_individual, mutated_individual, cr= 0.5):
        target_individual= target_individual.astype(int)
        min_len= min([len(target_individual), len(mutated_individual)])
        child= np.array([], dtype= int)
        for i in range(min_len):
            if random.random() < cr:
                child= np.append(child, mutated_individual[i])
            else:
                child= np.append(child, target_individual[i])
        fit_child= self.evaluate(child)
        fit_parent= self.evaluate(target_individual)
        if fit_child > fit_parent:
            return child
        else:
            return target_individual
    
    def run_algorithm(self, max_nfe= 1000):
        nfe= 0
        while nfe < max_nfe:
            for i in range(len(self.population)):
                mutated_individual= self.mutation(self.population, self.population[i])
                self.population[i]= self.crossover_selection(self.population[i], mutated_individual)
                nfe+= 1
        return self.population[np.argmax(self.fitness)], self.evaluate(self.population[np.argmax(self.fitness)])

# --> Thread pour Evaluation Parallèle <-- #
class GARatingThread(Thread):
    def __init__(self, agent, game):
        Thread.__init__(self)
        self.agent= agent
        self.game= game
        self.action= None
        self.isLeftCollision= None
        self.isRightCollision= None
    
    def attach_agents_strat(self, strategies):
        self.strategies= strategies

    def run(self, i):
        self.action= self.agent.select_action(self.agent.strategy[i])
        self.isLeftCollision, self.isRightCollision= self.game.capture_wall_collision(self.agent)

    def get_data(self):
        return self.action, self.isLeftCollision, self.isRightCollision
