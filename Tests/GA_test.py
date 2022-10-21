from typing import Container
import unittest
from SampleGeneticAlgorithm import SampleGA

class TestGa(unittest.TestCase):

    def setUp(self):
        self.POP_SIZE = 100
        self.NUM_GENES = 2

        # test fitness using Rosenbrock's function
        def fitness_function(x, y):
            return ((1 - x)**2 + 100*(y - x**2)**2)
    

        self.ga = SampleGA(fitness_func=fitness_function, num_genes=self.NUM_GENES, pop_size=self.POP_SIZE,
                           gene_lower_bound=-7, gene_upper_bound=15, select_pres=5, mutation_prob=0.5)

    def test_encode_gene_single(self):
        param = 1    
        result = self.ga.parameter_to_gene(param)
        self.assertEquals(result, "0001")
        
    def test_encode_gene_list(self):
        params = [1,2]
        result = self.ga.parameter_to_gene(params)
        self.assertEquals(result, None)

        genes = []
        for p in params:
            genes.append(self.ga.parameter_to_gene(p))
        self.assertEquals(genes, ["0001", "0010"])
        
    def test_gene_to_chromosome(self):
        params = [1,2]

        genes = []
        for p in params:
            genes.append(self.ga.parameter_to_gene(p))

        chromosome = self.ga.genes_to_chromosome(genes)
        self.assertEquals(chromosome, "00010010")

    def test_gene_to_parameter(self):
        gene = "0101"
        param = self.ga.gene_to_parameter(gene)
        self.assertEquals(param, 5)

        genes = ["0101", "1001"]
        result = self.ga.gene_to_parameter(genes)
        self.assertEquals(result, None)

        params = []
        for gene in genes:
            params.append(self.ga.gene_to_parameter(gene))
        self.assertEquals(params, [5, 9])

    def test_chromosome_to_genes(self):
        chromosome = "10010101"
        genes = self.ga.chromosome_to_genes(chromosome)
        self.assertEquals(genes, ["1001", "0101"])
        
        chromosome = "110010101"
        genes = self.ga.chromosome_to_genes(chromosome)
        self.assertEquals(genes, None)

    def test_generate_population(self):
        pop = self.ga.generate_population()
        # Check length of pop is correct
        self.assertEquals(len(pop), self.POP_SIZE)

        # Check length of each chromesome is correct    def test_tournament_selection(self):

        [self.assertEquals(len(c), (4*self.NUM_GENES)) for c in pop]

    def test_tournament_selection(self):
        pop = self.ga.initalize()
        # Best fitness determined via Rosenbrock function 
        best_fitness, best_chromosome = self.ga.tournament_selection()
        self.assertEquals(type(best_fitness), int)
        self.assertEquals(isinstance(best_chromosome, str), True)
        self.assertEquals(len(best_chromosome), 8)

    def test_crossover(self):
        p1 = "00010010"
        p2 = "11101101"
        c1, c2 = self.ga.crossover(p1, p2)
        self.assertNotEquals(c1, c2)

    def test_mutation(self):
        c = "00010010"

        c_m = self.ga.mutate(c)
        
    def test_run(self):
        self.ga.initalize()
        self.ga.run()