from pygame.sprite import *
import random
import numpy as np
from PIL import Image
from threading import Thread
from MenuWidget import MenuWidget
from Agent import Agent
import pygame

# --> Genetic Algorithm <-- #
HEIGHT= 900
WIDTH= 800
player_img= Image.open("Digital_Twin_Software\Software_Game_Assets\Player_car_final.png")
PLAYER_WIDTH, PLAYER_HEIGHT= player_img.size
class GeneticAlgorithm():
    def __init__(self, agents, evaluate, environment, isThreadEvaluation= False):
        print("Generation #0")
        print("-----------------------------")
        self.isThreadEvaluation= isThreadEvaluation
        self.agents= agents
        self.population = np.array([agent.strategy for agent in self.agents])
        self.l= self.population.shape[1]
        self.evaluate= evaluate
        self.isFinished= False
        self.max_nfe= 1000
        self.num_generation= 0
        self.environment= environment
        self.optimization_data= np.array([])

    def set_max_nfe(self, max_nfe):
        self.max_nfe= max_nfe
    
    def attach_menu(self, menu):
        self.menu= menu        

    def selection(self, t=2):
        #Implémenter le Tournament selection
        selected_indexs= random.sample(range(len(self.fitness)), t)
        selected_individual = np.argmin([self.fitness[i] for i in selected_indexs])
        return self.population[selected_individual]

    def recombination(self, parents):
        brk_points= random.sample([v for v in range(0, len(parents[0]))], len(parents)-1)
        sort_point= sorted(brk_points)
        rev_sort_point= sorted(brk_points, reverse= True)
        j= 0
        child1= []
        child2= []
        j= len(parents)
        for i in range(len(parents)):
            j -= 1
            if i == 0:
                child1= parents[i][:sort_point[i]]
                child2= parents[j][rev_sort_point[i]:]
            elif j == 0:
                child1= np.concatenate((child1, parents[i][sort_point[-1]:]), axis= None)
                child2= np.concatenate((parents[j][:rev_sort_point[-1]], child2), axis= None)
            else:
                child1= np.concatenate((child1, parents[i][sort_point[i-1]:sort_point[i]]), axis= None)
                child2= np.concatenate((parents[j][rev_sort_point[i]:rev_sort_point[i-1]], child2), axis= None)  
        return [child1, child2]

    def crossover(self, parent1, parent2):
        #Appeler la Tournament Selection 
        min_lenght= min(len(parent1), len(parent2))
        mid_len= int(min_lenght/2)
        brkpt1= random.randint(1, mid_len)
        """child1= np.concatenate((parent1[:brkpt1], parent2[brkpt1:]), axis= None)
        child2= np.concatenate((parent2[:brkpt1], parent1[brkpt1:]), axis= None)"""
        brkpt2= random.randint(mid_len, min_lenght-1)
        child1= np.concatenate((parent1[:brkpt1], parent2[brkpt1:brkpt2], parent1[brkpt2:]), axis= None)           # parent_1 -> | breakpoint | parent_2 ->
        child2= np.concatenate((parent2[:brkpt1], parent1[brkpt1:brkpt2], parent2[brkpt2:]), axis= None)            # parent_2 -> | breakpoint | parent_1 ->
    
        #Effectuer le crossover des parents sélectionnés
        return [child1, child2]

    def mutation(self, individual, p=0.1):
        #Implémenter une méthode de mutation
        for index_flip in range(len(individual)-1):
            if random.random() < p:
                individual[index_flip]= abs(1-individual[index_flip])   

        return individual

    def create_offspring(self, parents_strategies, num_recomb_parents= 0, t=2):
        offspring= np.empty((0, self.l))
        for i in range(len(parents_strategies)):
            if num_recomb_parents <= 0:
                parent1= self.selection(t)
                parent2= self.selection(t)
                childs= self.crossover(parent1, parent2)     
            else:
                parents= [self.selection(t) for i in range(num_recomb_parents)]
                childs= self.recombination(parents)

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
        best_index= np.argmin(self.fitness)
        if self.fitness[best_index] > 0:
            while k > 0:
                k-= 1
                best_index= np.argmin(self.fitness)
                new_generation= np.vstack((new_generation, self.population[best_index]))
                new_fitness= np.append(new_fitness, self.fitness[best_index])
                self.fitness= np.delete(self.fitness, best_index)
        new_generation= np.concatenate((new_generation, offspring_strategies[:pop_size-len(new_generation)]), axis= 0)
        new_fitness= np.concatenate((new_fitness, fitness_offspring[:pop_size-len(new_fitness)]), axis= None)
        self.population= np.array(new_generation)
        self.agents= [new_agent for new_agent in self.distribute_strategies(self.population)]
        self.menu.set_new_fitness(new_fitness)
        self.fitness= np.array(new_fitness)
        print("=============================")
        print("-> Fitness of New Generation= ", np.sort(self.fitness))
        print("=============================")
        #Remplir le reste population avec les individus de la nouvelle population

    def start_optimization(self):
        prev_best_fitness= 0
        if self.isThreadEvaluation:
            self.fitness= self.evaluate(self.agents)
        else:
            self.fitness = np.array(self.evaluate(self.agents))
        self.menu.set_init_fitness(self.fitness)
        nfe= 0
        nfe += len(self.population)
        self.show_best_agents(self.population, self.fitness, num_agents= len(self.population))
        while nfe < self.max_nfe:
            print("-----------------------------")
            print("==> Generation #" + str(self.num_generation))
            print("-----------------------------")
            if prev_best_fitness == np.max(self.fitness):
                if self.num_generation % 3 == 0:
                    offspring= self.create_offspring(parents_strategies= self.population, num_recomb_parents= 4, t= 12)
                else:
                    offspring= self.create_offspring(parents_strategies= self.population, num_recomb_parents= 4, t= 3)
            else:
                offspring= self.create_offspring(parents_strategies= self.population, num_recomb_parents= 4, t= 6)
            nfe += len(offspring)
            self.replacement(self.population, offspring, k= int(self.population.shape[0]//5))
            if self.num_generation % 10 == 0:
                self.show_best_agents(self.population, self.fitness, num_agents= 15)
            if self.num_generation % 20 == 0:
                prev_best_fitness= np.max(self.fitness)
            self.num_generation += 1
        best_index= np.argmax(self.fitness)
        self.show_best_agents(self.population, self.fitness, num_agents= 1)
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
    
    def show_best_agents(self, strategies, fitnesses, num_agents= 15):
        self.environment.clock.tick(20)
        best_fit= np.sort(fitnesses)[:num_agents]
        indexs= np.array([])
        ind= np.array([])
        for fit in best_fit:
            ind= np.where(fitnesses == fit)[0]
            if len(ind) > num_agents:
                ind= ind[:num_agents]
                num_agents= 0
            indexs= np.concatenate((indexs, ind), axis= None)
            num_agents -= len(ind)
            if num_agents <= 0:
                break
        indexs= indexs.astype(int)
        agents_created= np.array([Agent(velocity= 10, rotation_angle= 45, 
                                    position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                    skin= "Software_Game_Assets/car1.png") for i in range(len(indexs))], dtype= Agent)
        for i, index in enumerate(indexs):
            agents_created[i].strategy= strategies[index]
        agents= Group([agent for agent in agents_created])
        agents.draw(self.menu.window)
        pygame.display.update()
        stop_eval_array= [False for i in range(len(agents_created))]
        for j in range(strategies.shape[1]):
            for z, agent in enumerate(agents_created):
                if stop_eval_array[z] == False:
                    collided_sprites= pygame.sprite.spritecollide(agent, self.environment.STATIC_SPRITES, False)
                    if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                        stop_eval_array[z]= True
                    elif len(collided_sprites) != 0 and self.environment.FINISH_LINE not in collided_sprites:
                        stop_eval_array[z]= True
                    elif self.environment.FINISH_LINE in collided_sprites:
                        stop_eval_array[z]= True
                    action= agent.select_action(agent.strategy[j])
                agents= Group([agents_created[k] for k in range(len(agents_created)) if stop_eval_array[k] == False])
                self.menu.window.fill((255,255,255))
                self.environment.STATIC_SPRITES.draw(self.menu.window)
                agents.draw(self.menu.window)
                pygame.display.update()
                if len(agents) == 0:
                    break
            if len(agents) == 0:
                break
            for event in pygame.event.get():
                pass

class NSGAII():
    def __init__(self, agents, n_obj_evaluate, environment, menu, max_nfe= 1000):
        self.evaluate= n_obj_evaluate
        agents_strategies= np.array([agent.strategy for agent in agents])
        self.population= {i: {"agent": agents[i], "strategy": agents_strategies[i], "steps_score": 0, "global_score":0} for i in range(len(agents_strategies))}
        self.max_nfe= max_nfe
        self.num_generation= 0
        self.environment= environment
        self.menu= menu
        self.isFinished= False
        self.isFirstStep= True
    
    #-> Preprocessing Population
    def isDominant(self, main_individual, second_individual):
        if main_individual["steps_score"] <= second_individual["steps_score"] and main_individual["global_score"] < second_individual["global_score"]:
            return True
        else:
            return False
        
    def find_worst_front(self, population):
        front= {}
        solutions= {key: {"dominated_solutions":{}, "dominated_count":0} for key in population.keys()}
        for i in population.keys():
            main_individual= population[i]
            for j in population.keys():
                second_individual= population[j]
                if i == j:
                    continue
                if self.isDominant(main_individual, second_individual):
                    solutions[i]["dominated_solutions"][j]= second_individual
                    solutions[i]["dominated_count"] += 1
            if solutions[i]["dominated_count"] == 0:
                front[i]= main_individual
        return front


    def get_pareto_front_ranking(self, population):
        pop= population
        derank_population= {}
        rank_population= {}
        front= set()
        p= 0
        while len(pop.keys()) > 0:
            front= self.find_worst_front(pop)
            derank_population[p]= front
            p += 1
            for indiv in front.keys():
                del pop[indiv]
        """while p in rank_population.keys():
            pareto_front= {}
            for indiv in rank_population[p].keys():
                for dominated in solutions[indiv]["dominated_solutions"].keys():
                    solutions[dominated]["dominated_count"] -= 1
                    if solutions[dominated]["dominated_count"] == 0:
                        pareto_front[dominated]= solutions[dominated]
            p += 1
            if len(pareto_front) != 0:
                rank_population[p]= pareto_front"""
        for i, key in enumerate(sorted(derank_population.keys(), reverse= True)):
            rank_population[i]= derank_population[key]
            for indiv in derank_population[key].keys():
                rank_population[i][indiv]["pareto_label"]= i
        return rank_population
    
    def crowding_distance_rank(self, ranked_front, start_index= 0):
        ranked_pareto_front= {i+start_index:ranked_front[indiv] for i, indiv in enumerate(ranked_front.keys())}
        prec_indiv= 0
        for i in range(1, len(ranked_pareto_front.keys())-1):
            k= i+start_index
            main_indiv= ranked_pareto_front[k]
            main_dist= abs(ranked_pareto_front[k-1]["steps_score"] - ranked_pareto_front[k+1]["steps_score"]) + abs(ranked_pareto_front[k-1]["global_score"] - ranked_pareto_front[k+1]["global_score"])
            for j in range(k+1, len(ranked_pareto_front.keys())-1):
                second_indiv= ranked_pareto_front[j]
                second_dist= abs(ranked_pareto_front[j-1]["steps_score"] - ranked_pareto_front[j+1]["steps_score"]) + abs(ranked_pareto_front[j-1]["global_score"] - ranked_pareto_front[j+1]["global_score"])
                if second_dist > main_dist:
                    ranked_pareto_front[k]= second_indiv
                    ranked_pareto_front[j]= main_indiv
        return ranked_pareto_front

    #-> Steps of Algorithm
    def selection(self, population, t= 2):
        selected_indexs= random.sample(range(len(population.keys())), t)
        return population[np.argmin(selected_indexs)]
    
    def crossover(self, parent1, parent2):
        #Appeler la Tournament Selection 
        parent1_strat= parent1["strategy"]
        parent2_strat= parent2["strategy"]
        min_lenght= min(len(parent1_strat), len(parent2_strat))
        mid_len= int(min_lenght/2)
        brkpt1= random.randint(1, mid_len)
        """child1= np.concatenate((parent1[:brkpt1], parent2[brkpt1:]), axis= None)
        child2= np.concatenate((parent2[:brkpt1], parent1[brkpt1:]), axis= None)"""
        brkpt2= random.randint(mid_len, min_lenght-1)
        child1_agent= Agent(velocity= 10, rotation_angle= 45, 
                                    position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                    skin= "Software_Game_Assets/car1.png")
        child1_agent.strategy= np.concatenate((parent1_strat[:brkpt1], parent2_strat[brkpt1:brkpt2], parent1_strat[brkpt2:]), axis= None)           # parent_1 -> | breakpoint | parent_2 ->
        child2_agent= Agent(velocity= 10, rotation_angle= 45, 
                                    position= ((WIDTH/2) - (PLAYER_WIDTH / 2), HEIGHT - (PLAYER_HEIGHT/1.7)),
                                    skin= "Software_Game_Assets/car1.png")
        child2_agent.strategy= np.concatenate((parent2_strat[:brkpt1], parent1_strat[brkpt1:brkpt2], parent2_strat[brkpt2:]), axis= None)            # parent_2 -> | breakpoint | parent_1 ->
    
        #Effectuer le crossover des parents sélectionnés
        return {"agent": child1_agent, "strategy": child1_agent.strategy, "steps_score": 0, "global_score":0}, {"agent": child2_agent, "strategy": child2_agent.strategy, "steps_score": 0, "global_score":0}

    def mutation(self, individual, p=0.15):
        #Implémenter une méthode de mutation
        strategy= individual["strategy"]
        for index_flip in range(len(strategy)-1):
            if random.random() < p:
                strategy[index_flip]= abs(1-strategy[index_flip])   
        individual["strategy"]= strategy
        return individual
    
    def create_offspring(self, population, t= 2):
        offspring= {}
        k=len(population.keys())
        pop_ranked= {}
        start_index= 0
        ranking= self.get_pareto_front_ranking(population)
        for i in range(len(ranking.keys())):
            ranked_front= self.crowding_distance_rank(ranking[i], start_index= start_index)
            start_index+= len(ranked_front.keys())
            pop_ranked= pop_ranked | ranked_front
        for id in pop_ranked.keys():
            parent1= self.selection(pop_ranked, t)
            parent2= self.selection(pop_ranked, t)
            child1, child2= self.crossover(parent1, parent2)
            child1= self.mutation(child1)
            child2= self.mutation(child2)
            offspring[k]= child1
            offspring[k+1]= child2
            k+=2
        return offspring
    
    def replacement(self, population, offspring):
        new_generation= {}
        new_steps_scores, new_global_scores= self.evaluate([offspring[id]["agent"] for id in offspring.keys()])
        i=0
        for id in offspring.keys():
            offspring[id]["steps_score"]= new_steps_scores[i]
            offspring[id]["global_score"]= new_global_scores[i]
        full_ranking= self.get_pareto_front_ranking(population | offspring)
        pop_size= len(population.keys())
        j= 0
        printed_fitness= np.zeros((pop_size, 2))
        while j < pop_size:
            for front in full_ranking.keys():
                if j + len(full_ranking[front]) < pop_size:
                    for indiv in full_ranking[front]:
                        new_generation[j]= full_ranking[front][indiv]
                        printed_fitness[j]= [full_ranking[front][indiv]["steps_score"], full_ranking[front][indiv]["global_score"]]
                        j+=1
                else:
                    ranking_front= self.crowding_distance_rank(full_ranking[front])
                    for individual in ranking_front.keys():
                        if j < pop_size:
                            new_generation[j]= ranking_front[individual]
                            printed_fitness[j]= [ranking_front[individual]["steps_score"], ranking_front[individual]["global_score"]]
                        else:
                            break
                        j+=1
        """if self.num_generation % 10 == 0:
            if printed_fitness[0,1] <= 450:
                self.isFirstStep= False
            self.last_gscore= printed_fitness[-1,1]"""
        print("=============================")
        print("-> Fitness of New Generation= ")
        print(printed_fitness[0:pop_size//2, :])
        print("=============================")
        return new_generation
                         
    def start_optimization(self):
        steps_scores, global_scores= self.evaluate([self.population[id]["agent"] for id in self.population.keys()])
        for id in self.population.keys():
            self.population[id]["steps_score"]= steps_scores[id]
            self.population[id]["global_score"]= global_scores[id]
        population= self.population
        nfe= 0
        nfe += len(self.population)
        self.show_best_agents(self.population, len(self.population))
        while nfe < self.max_nfe:
            print("-----------------------------")
            print("==> Generation #" + str(self.num_generation))
            print("-----------------------------")
            offspring= self.create_offspring(population.copy(), t= 2)
            nfe += len(offspring.keys())
            population= self.replacement(population.copy(), offspring.copy())
            self.num_generation+=1
            if self.num_generation % 10 == 0:
                self.show_best_agents(population, 20)
        self.show_best_agents(population, num_agents= 1)
        self.isFinished= True
        return population[0]

    def show_best_agents(self, population, num_agents= 10):
        best_agents= []
        self.environment.clock.tick(20)
        for id in range(num_agents):
            population[id]["agent"].reset_state()
            best_agents.append(population[id]["agent"])
        num_actions= len(best_agents[0].strategy)
        agents= Group([agent for agent in best_agents])
        agents.draw(self.menu.window)
        stop_eval_array= [False for i in range(len(best_agents))]
        self.menu.window.fill((255,255,255))
        self.environment.STATIC_SPRITES.draw(self.menu.window)
        agents.draw(self.menu.window)
        pygame.display.update()
        for i in range(num_actions):
            for z, agent in enumerate(best_agents):
                if stop_eval_array[z] == False:
                    collided_sprites= pygame.sprite.spritecollide(agent, self.environment.STATIC_SPRITES, False)
                    if (agent.rect.top > 900 or agent.rect.bottom > 900) or (agent.surf.top > 900 or agent.surf.bottom > 900):
                        stop_eval_array[z]= True
                    elif len(collided_sprites) != 0 and self.environment.FINISH_LINE not in collided_sprites:
                        stop_eval_array[z]= True
                    elif self.environment.FINISH_LINE in collided_sprites:
                        stop_eval_array[z]= True
                    action= agent.select_action(agent.strategy[i])
            agents= Group([best_agents[k] for k in range(len(best_agents)) if stop_eval_array[k] == False])
            self.menu.window.fill((255,255,255))
            self.environment.STATIC_SPRITES.draw(self.menu.window)
            agents.draw(self.menu.window)
            pygame.display.update()
            if len(agents) == 0:
                    break
            if len(agents) == 0:
                break
            for event in pygame.event.get():
                pass
            



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