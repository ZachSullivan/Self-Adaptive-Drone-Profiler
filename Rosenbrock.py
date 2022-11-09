"""Tests GA class with finding root of a Rosenbrock function optimal solution should be located at (1,1)"""
from SampleGeneticAlgorithm import SampleGA
from GAv5 import GA
import matplotlib.pyplot as plt

# Test fitness using Rosenbrock's function
def fitness_function(params):
    x = params[0]
    y = params[1]
    return ((1 - x)**2 + 100*(y - x**2)**2)


#ga = SampleGA(fitness_func=fitness_function, num_genes=2, pop_size=8,
#             gene_lower_bound=-127, gene_upper_bound=127, select_pres=4, mutation_prob=0.05, generations=50)

#ga = GA(fitness_function=fitness_function, num_genes=2, gene_min=-127, gene_max=127, bit_size=8, pop_size=100, t_size = 5, mu=0.05, gens=10)
ga = GA(fitness_function, fitness_shape=[-3.5,3.5,2,4], pop_size=10, k=3, gen_count=5, mu=0.05)
ga.initialize()

fig, ax = plt.subplots()
for i in range(10):

    best_params, best_fitness = ga.run()
    print("> Best Solution:{0} W/ score: {1}\n".format(
                    best_params, best_fitness))

    winners = ga.gen_winners

    ax.plot(range(0, len(winners)), winners)
plt.legend()
plt.xlabel("Generations")
plt.ylabel("Optimization Score")
plt.title("Finding Rosenbrock Root with 2^255 combinations")
plt.show()