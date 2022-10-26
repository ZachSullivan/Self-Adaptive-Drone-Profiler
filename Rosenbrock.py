"""Tests GA class with finding root of a Rosenbrock function optimal solution should be located at (1,1)"""
from SampleGeneticAlgorithm import SampleGA
from GAv4 import GA
import matplotlib.pyplot as plt

# Test fitness using Rosenbrock's function
def fitness_function(params):
    return ((1 - params[0])**2 + 100*(params[1] - params[0]**2)**2)


#ga = SampleGA(fitness_func=fitness_function, num_genes=2, pop_size=8,
#             gene_lower_bound=-127, gene_upper_bound=127, select_pres=4, mutation_prob=0.05, generations=50)

ga = GA(fitness_function=fitness_function, num_genes=2, gene_min=-127, gene_max=127, bit_size=8, pop_size=100, t_size = 5, mu=0.05, gens=10)


ga.initalize()
best_params, best_fitness = ga.run()
print("> Best Solution:{0} W/ score: {1}\n".format(
                best_params, best_fitness))

winners = ga.get_winners()
fig, ax = plt.subplots()
plt.plot(range(0, len(winners)), winners)
plt.xlabel("Generations")
plt.ylabel("Optimization Score")
plt.title("Finding Rosenbrock Root with 2^255 combinations")
plt.show()