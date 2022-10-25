"""Debug"""
from multiprocessing.sharedctypes import Value
import random
import numpy as np
import progressbar


class SampleGA():
    def __init__(self, fitness_func, num_genes=2, pop_size=10, gene_upper_bound=10, gene_lower_bound=10, select_pres=5, generations=10, mutation_prob=0.03) -> None:
        super().__init__()
        # The number of genes in any given chromosome, number of genes should == number of action leafs
        self.num_genes = num_genes
        if gene_upper_bound <= 127 and gene_lower_bound >= -127:
            self.gene_upper_bound = gene_upper_bound
            self.gene_lower_bound = gene_lower_bound
        else:
            raise ValueError("Gene range bounded to 8 bit values")

        self.pop_size = pop_size  # The population size of an inital population
        self.generations = generations  # The number of generations to iterate over
        self.population = []  # Population records all current chromosomes

        # Fitness function that computes/simulates a score
        self.fitness_func = fitness_func

        self.k = select_pres
        self.mu = mutation_prob
        self.scores_table = {}
        self.winners = []   # List of winners from each generation
    # Encodes a given parameter as a gene in binary

    def parameter_to_gene(self, p):
        try:
            if p >= 0:
                return ''.join([format(0, "04b"), format(p, "08b")])
                #return format(p, "08b")
            elif p < 0:
                return ''.join([format(1, "04b"), format(abs(p), "08b")])
            else:
                raise TypeError("Signed values unsupported")

        except TypeError:
            print(
                "Unsupported type provided, encode_param only supports non-iterable int")
            return None

        # Decodes a single gene in binary to a parameter in decimal base 10
    def gene_to_parameter(self, g):
        try:
            if bool(int(g[:4])) == True:
                return int(g[4:], 2) * -1
            else:
                return int(g[4:], 2)
        except TypeError:
            print(
                "Unsupported Type provided, gene_to_parameter only supports non-iterable int")
            return None

    # Concatenates a list of genes as a bitstring chromosome
    def genes_to_chromosome(self, genes):
        return "".join([g for g in genes])

    # Deconstucts a bitstring chromosome into its consituent binary genes
    # Note each gene is 4 bits long
    def chromosome_to_genes(self, c):
        try:
            if len(c) % 8 != 0:
                raise ValueError("chromosome length is not a multiple of 4")

            splice_len = int(len(c)/self.num_genes)

            return [c[i:i+splice_len] for i in range(0, len(c), splice_len)]
        except ValueError:
            return None

    # Generates an inital population of chromosomes
    def generate_population(self):
        pop = []
        for i in range(self.pop_size):
            parameters = [random.randint(
                self.gene_lower_bound, self.gene_upper_bound) for i in range(self.num_genes)]
            genes = [self.parameter_to_gene(p) for p in parameters]
            chromosome = self.genes_to_chromosome(genes)
            pop.append(chromosome)
        return pop

    # Select N number of chromosomes at random, score fitness and store best fit
    def tournament_selection(self):
        best_fitness = None
        best_chromosome = None

        for i in range(self.k):
            c = self.population[random.randint(0, len(self.population)-1)]
            genes = self.chromosome_to_genes(c)
            parameters = [self.gene_to_parameter(g) for g in genes]
            if c not in self.scores_table.keys():
                #fitness = self.fitness_func(parameters)
                fitness = self.fitness_func(parameters[0], parameters[1])
                self.scores_table.update({c: fitness})
            else:
                fitness = self.scores_table[c]
            if best_fitness is None or fitness < best_fitness:
                best_fitness = fitness
                best_chromosome = c
        return best_fitness, best_chromosome

    # Take two parent chromosomes, perform singlepoint crossover return two children
    def crossover(self, p1, p2):

        if len(p1) != len(p2):
            raise ValueError("Parent chromosomes are mismatched lengths.")

        cross_point = random.randint(0, len(p1)-1)

        p1_list = list(p1)
        p2_list = list(p2)
        c1 = (p1_list[:cross_point] + p2_list[cross_point:])
        c2 = (p1_list[cross_point:] + p2_list[:cross_point])

        return c1, c2

    # Mutates a given chromosome with probability mu
    def mutate(self, chromosome):
        c_copy = list(chromosome)
        for allele_i, allele in enumerate(chromosome):
            #try:
            if random.random() < self.mu:
                c_copy[allele_i] = str(int(allele) ^ 1)
            #except TypeError:
            #    continue
        return ("".join(c_copy))

    # Initalize the GA with a starting population and generation
    def initalize(self):
        self.population = [np.random.randint(0, 2, self.bit_count).tolist() for _ in range(self.pop_size)]

        #self.population = self.generate_population()

    def run(self):

        if self.population is None or len(self.population) <= 0:
            raise ValueError(
                "Starting population was not initalized before run.")

        best_chromosome = None
        best_params = None
        best_fitness = None
        for generation in range(self.generations):
            # Create empty future population
            future_pop = []
            scores = []
 
            bar = progressbar.ProgressBar(maxval=progressbar.UnknownLength)
            # while length of future population does not meet the specifed population size

            while len(future_pop) < self.pop_size:

                # select best parent 1 via Tournament Selection using current population
                p1_fitness, parent1 = self.tournament_selection()
                # select best parent 2 via Tournament Selection using current population
                p2_fitness, parent2 = self.tournament_selection()

                scores.extend([(p1_fitness, parent1), (p2_fitness, parent2)])

                # Crossover parent 1 and 2 produce child 1 and child 2
                child1, child2 = self.crossover(parent1, parent2)

                # Mutate child 1 and child 2
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # Add child 1, child 2, parent 1 and parent 2 to future population
                #future_pop.extend([parent1, parent2, child1, child2])
                future_pop.extend([child1, child2])
                
                # Debug progress bar
                bar.update(len(future_pop))

            for score in scores:
                if best_fitness is None or score[0] < best_fitness:
                    best_fitness = score[0]
                    best_chromosome = score[1]
                    genes = self.chromosome_to_genes(best_chromosome)
                    best_params = [self.gene_to_parameter(g) for g in genes]

            bar.finish()
            self.winners.append(best_fitness)
            print("> Generation:{0}, winning parameter: ({1}) W/ score: {2}\n".format(
                generation,  best_params, best_fitness))

            self.population = future_pop

        return best_params, best_fitness

    # Returns a list of winners over len(list) number of generations
    def get_winners(self):
        return self.winners