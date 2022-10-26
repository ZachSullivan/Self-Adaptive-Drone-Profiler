import numpy as np

class GA():
    def __init__(self, fitness_function, num_genes, gene_min, gene_max, bit_size, pop_size, t_size, mu, gens) -> None:
        self.fitness_func = fitness_function
        self.num_genes = num_genes
        self.bounds = [gene_min, gene_max]
        self.bit_size = bit_size
        self.mu = mu
        self.pop_size = pop_size 
        self.generations = gens
        self.k = t_size

        self.population = []
        self.scores = []
        self.winners = []

    def tournament_selection(self):

        for i in range(self.k):
            best = np.random.randint(len(self.population)-1)

            for i in range(self.pop_size):
                if self.scores[i] < self.scores[best]:
                    best = i
        return self.population[best]
           
    def crossover(self, p1, p2):
        if len(p1) != len(p2):
            raise ValueError("Parent chromosomes are mismatched lengths.")

        cross_point = np.random.randint(0, len(p1)-1)

        c1 = (p1[:cross_point] + p2[cross_point:])
        c2 = (p1[cross_point:] + p2[:cross_point])

        return c1, c2

    def mutate(self, c):
        c_mu = c.copy()
        for allele in range(0, len(c)-1):
            if np.random.random() < self.mu:
                c_mu[allele] = (c[allele]^1)
        return c_mu

    # Returns a list of winners over len(list) number of generations
    def get_winners(self):
        return self.winners

    def chromosome_to_params(self, c):
        params = list()
        # Iterate over each gene in the chromosome
        for i in range(0, self.bit_size*self.num_genes, self.bit_size):
            gene_str = ''.join(str(a) for a in c[i:(self.bit_size+i)])
            gene = int(gene_str, 2)
            # Normalize gene to [0, 1]:
            max_gene = ((2**self.bit_size)-1)/2
            min_gene = -(max_gene)
            gene_normalized = (gene - min_gene) / (max_gene - min_gene)

            # Then scale normalized gene to [x,y] rangebound:
            param = (gene_normalized * (self.bounds[1] - self.bounds[0])) + self.bounds[0]
            params.append(param)
        return params

    def initalize(self):
        self.population = [np.random.randint(0, 2, self.bit_size*self.num_genes).tolist() for _ in range(self.pop_size)]
    
    def run(self):
        best_fitness, best = None, None
        for gen in range(self.generations):
            params = [self.chromosome_to_params(chromosome) for chromosome in self.population]
            self.scores = [self.fitness_func(param) for param in params]
            
            for score_i, score in enumerate(self.scores):
                if best_fitness is None or score < best_fitness:
                    best_fitness = score
                    best = self.chromosome_to_params(self.population[score_i])
                    
            children = list()

            for i in range(0, self.pop_size, 2):
                p1, p2 = [self.tournament_selection() for p in range(2)]
                c1, c2 = self.crossover(p1, p2)

                c1 = self.mutate(c1)
                c2 = self.mutate(c2)

                children.extend([c1, c2])

            self.population = children
            self.winners.append(best_fitness)
            print("> Generation:{0}, winning parameter: ({1}) W/ score: {2}\n".format(
                gen,  best, best_fitness))

        return [best, best_fitness]