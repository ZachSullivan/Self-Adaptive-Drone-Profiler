from multiprocessing.sharedctypes import Value

import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class GA():
    """
    Defines a custom Genetic Algorithm

    Args: 
    fitness_function(:method:): A user defined function to evaulate an inidvidual's fitness or cost 
    fitness_shape(:list:): Takes 4 subarguments, upper and lower range bound of the search space, the parameter count needed for the fitness function, and the resolution of the fitness
    pop_size(:int:): The population target of each generation
    k(:int:): The non-negative selection pressume exerted by the tournament selector (higher values increase speed of convergence, but raise likelyhood local minimum trapping)
    gen_count(:int:): The number of generations simulated before termination
    mu(:int:): The non-negative probability for mutation to occur
    """
    def __init__(self, fitness_function, pop_size, use_lookup = True, fitness_shape=[-1,1,2,2], k=3, gen_count=10, mu=0.05) -> None:
        self.fitness_function = fitness_function
        
        self.lower_gene_bound = fitness_shape[0]
        self.upper_gene_bound = fitness_shape[1]
        self.gene_count = fitness_shape[2]
        self.precision = fitness_shape[3]
        
        self.use_lookup = use_lookup

        self.gene_len = 8
        self.chromosome_len = self.gene_len * self.gene_count

        self.pop_size = pop_size
        self.population = list()
        self.k = k
        self.gen_count = gen_count

        if mu > 1 or mu < 0:
            raise ValueError("Mutation rate must be between 0 and 1")
        self.mu = mu

        # Lookup table that stores chromosome keys to fitness values
        self.fitness_table = dict()
        self.gen_winners = list()

    # initialize the first generation, with population of zero'd chromosomes then mutating
    def initialize(self):

        zeroed_pop = [([0] * self.chromosome_len)] * self.pop_size
        self.population = [self.mutate(c, 0.75) for c in zeroed_pop]
        #self.population = np.random.randint(2, size=(self.pop_size, self.chromosome_len)).tolist()

        for p in self.population:
            print(str(self.chromosome_to_params(p)))

    def mutate(self, c, mu=0.05):
        c_copy = c.copy()
        for i, allele in enumerate(c):
            if np.random.random_sample() < mu:
                c_copy[i] = allele ^ 1
        return c_copy

    def chromosome_to_params(self, c):
        params = list()
        genes = list()
        for i in range(0, self.chromosome_len, 8):
            genes.append(''.join(str(a) for a in c[i:(8+i)]))

        # Iterate over each gene in the chromosome
        for g in genes:
            g = int(g, 2)
            # Normalize gene to [0, 1]:
            max_gene = ((2**self.gene_len)-1)/2
            min_gene = -(max_gene)

            # If g exceeds max gene, then the overflow becomes the negative seed value 
            if g > max_gene:
                g = max_gene - g
               
            gene_normalized = (g - min_gene) / (max_gene - min_gene)

            # Then scale normalized gene to [x,y] rangebound:
            param = (gene_normalized * (self.upper_gene_bound - self.lower_gene_bound)) + self.lower_gene_bound
            params.append(round(param, self.precision))
        return params

    def evaluate(self, c):
        params = self.chromosome_to_params(c)
        key = (''.join(str(a) for a in c))

        if self.use_lookup == True:
            if key not in self.fitness_table.keys():
                self.fitness_table[key] = self.fitness_function(params)
        else:
            self.fitness_table[key] = self.fitness_function(params)

        return self.fitness_table[key]

    def tournament_selection(self):

        for i in range(self.k):
            if len(self.population) > 1:
                c_idx = np.random.randint(len(self.population)-1)
            else:
                c_idx = np.random.randint(1)
            best_chromosome = self.population[c_idx]
            best_score = self.evaluate(best_chromosome)
            for j in self.population:
                score = self.evaluate(j)
                if score < best_score:
                    best_chromosome = j

        return best_chromosome

    def crossover(self, p1, p2):
        if len(p1) != len(p2):
            raise ValueError("Parent chromosomes are mismatched lengths.")

        cross_point = np.random.randint(0, len(p1)-1)

        c1 = (p1[:cross_point] + p2[cross_point:])
        c2 = (p1[cross_point:] + p2[:cross_point])

        return c1, c2

    def visualize(self):
        fig, ax = plt.subplots()

        X = []
        Y = []
        Z = list(self.fitness_table.values())

        for c in self.fitness_table.keys():
            params = self.chromosome_to_params(c)
            X.append(params[0])
            Y.append(params[1])
        
        df = pd.DataFrame(list(zip(X, Y, Z)), columns=["take_off_vel", "flight_vel", "score"])
        #ax.pcolormesh([X,Y], cmap="autumn")
        print(df)
        # generating pairwise correlation
        corr = df.corr()
        sns.heatmap(corr, annot = True)
        
        sns.relplot(
            data=df,
            x='take_off_vel', y='flight_vel',
            size='score', sizes=(10, 100),
            hue='score',
            palette='coolwarm',
        )

        plt.show()

    def save_population_to_csv(self, population, generation):
        # Open a new CSV file for writing
        filename = f'adaptive_profiler_data.csv'
        with open(filename, mode='a') as csv_file:
            # Create a CSV writer object
            writer = csv.writer(csv_file)

            # Add a new table to the CSV file for the current generation
            writer.writerow([f'Generation {generation}'])

            # Write the header row for the table
            writer.writerow(['Individual', 'Takeoff Velocity', 'Flight Velocity', 'Posture Cost'])

            # Write the individual rows for the population
            for i, individual in enumerate(population):
                posture_cost = self.evaluate(individual)
                params = self.chromosome_to_params(individual)
                writer.writerow([i, params[0], params[1], posture_cost])
        csv_file.close()

    def run(self):
        best_p, best_fitness = None, None

        for generation in range(self.gen_count):

            next_pop = list()


            """for p in self.population:
                print("SIIMULATING: " + str(self.chromosome_to_params(p)))
                self.evaluate(p)"""

            for i in range(0, self.pop_size, 2):

                # select best parent 1 via Tournament Selection using current population
                p1 = self.tournament_selection()
                p2 = self.tournament_selection()

                # Crossover parent 1 and 2 produce child 1 and child 2
                c1, c2 = self.crossover(p1, p2)

                # Mutate child 1 and child 2
                c1 = self.mutate(c1, self.mu)
                c2 = self.mutate(c2, self.mu)

                # Add child 1, child 2, parent 1 and parent 2 to future population
                next_pop.extend([c1, c2])

            for key, value in self.fitness_table.items():
                if best_fitness is None or value < best_fitness:
                    best_fitness = value
                    c = [int(i) for i in list(key)]
                    best_p = self.chromosome_to_params(c)

            print("> Generation:{0}, winning parameter: ({1}) W/ score: {2}\n".format(
                generation, best_p, best_fitness))

            self.gen_winners.append(best_fitness)

            self.population = next_pop

            # Save population to csv
            self.save_population_to_csv(self.population, generation)
        return best_p, best_fitness
