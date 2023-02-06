import random
import numpy as np

# --> Genetic Algorithm <-- #
class GeneticAlgorithm():
    def __init__(self, population, evaluate):
        self.population = population
        self.l= population.shape[1]
        self.evaluate= evaluate
        self.fitness = np.array([self.evaluate(individual) for individual in self.population])

    def selection(self, t=2):
        #Implémenter le Tournament selection
        selected_indexs= random.sample(range(len(self.fitness)), t)
        selected_individual = np.argmax([self.fitness[i] for i in selected_indexs])
        return self.population[selected_individual]
        
    def crossover(self, parent1, parent2):
        #Appeler la Tournament Selection 
        min_lenght= min(len(parent1), len(parent2))
        brkpt= random.randint(1, min_lenght-1)
        child1= np.concatenate((parent1[:brkpt], parent2[brkpt:]), axis= None)           # parent_1 -> | breakpoint | parent_2 ->
        child2= np.concatenate((parent1[:brkpt], parent2[brkpt:]), axis= None)            # parent_2 -> | breakpoint | parent_1 ->
        #Effectuer le crossover des parents sélectionnés
        return [child1, child2]

    def mutation(self, individual, p=0.1):
        #Implémenter une méthode de mutation
        for index_flip in range(len(individual)):
            if random.random() < p:
                individual[index_flip]= abs(1-individual[index_flip])
        return individual

    def create_offspring(self, parents_population, t=2):
        offspring= np.empty((0, self.l))
        for i in range(len(parents_population)):
            parent1= self.selection(t)
            parent2= self.selection(t)
            childs= self.crossover(parent1, parent2)
            childs= np.array([self.mutation(child) for child in childs])
            offspring= np.concatenate((offspring, childs), axis= 0)
        return offspring

    def replacement(self, parents_population, offspring_population, k= 5):
        parents_population= parents_population.astype(int)
        offspring_population= offspring_population.astype(int)
        new_generation= np.empty((0, parents_population.shape[1]))
        new_fitness= np.array([])
        pop_size= len(parents_population)
        #Evaluer la nouvelle population(Offspring)
        fitness_offspring= np.array([self.evaluate(individual) for individual in offspring_population])
        #Elitisme --> garder les K meilleurs individus de la Génération précédente
        while k > 0:
            k-= 1
            best_index= np.argmax(self.fitness)
            new_generation= np.vstack((new_generation, self.population[best_index]))
            new_fitness= np.append(new_fitness, self.fitness[best_index])
            self.fitness= np.delete(self.fitness, best_index)
        new_generation= np.concatenate((new_generation, offspring_population[:pop_size-len(new_generation)]), axis= 0)
        new_fitness= np.concatenate((new_fitness, fitness_offspring[:pop_size-len(new_fitness)]), axis= None)
        self.population= np.array(new_generation)
        self.fitness= np.array(new_fitness)
        #Remplir le reste population avec les individus de la nouvelle population
    
    def run_algorithm(self, max_nfe= 1000):
        nfe= 0
        nfe += len(self.population)
        while nfe < max_nfe:
            offspring= self.create_offspring(self.population)
            self.replacement(self.population, offspring)
            nfe += len(offspring)
        best_index= np.argmax(self.fitness)
        return self.population[best_index], self.fitness[best_index]

# --> Differential Evolution Algorithm <-- #
class DifferentialEvolution:
    def __init__(self, population, evaluate):
        self.population = population
        self.l= population.shape[1]
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
