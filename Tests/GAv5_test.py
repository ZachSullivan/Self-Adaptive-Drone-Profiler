from ast import IsNot
from GAv5 import GA
import unittest

class GATest(unittest.TestCase):

    def setUp(self):

        # Global minimum exists at (1,1)=0
        def rosenbrock_fitness(params):
            x, y = params[0], params [1]
            return ((1 - x)**2 + 100*(y - x**2)**2)

        self.upper_gene = 3
        self.lower_gene = -3
        self.pop_size = 10
        self.chromosome_len = 16
        self.k=3
        self.gens = 10

        self.ga = GA(rosenbrock_fitness, self.upper_gene, self.lower_gene,
                     self.pop_size, self.chromosome_len, self.k, self.gens)

    def test_intialization(self):
        self.ga.intialize()
        self.assertEquals(len(self.ga.population), 10)
        for c in self.ga.population:
            self.assertAlmostEquals(len(c), self.chromosome_len)