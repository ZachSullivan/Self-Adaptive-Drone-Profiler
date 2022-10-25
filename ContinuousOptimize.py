from GAv4 import GA
import matplotlib.pyplot as plt

def fitness_function(params):
   return (params[0]**2.0 + params[1]**2.0)

ga = GA(fitness_function=fitness_function, num_genes=2, gene_min=-5, gene_max=5, bit_size=16, pop_size=100, mu=0.05, gens=100)

ga.initalize()
best_params, best_fitness = ga.run()
print("> Best Solution:{0} W/ score: {1}\n".format(
                best_params, best_fitness))

winners = ga.get_winners()
fig, ax = plt.subplots()
plt.scatter(range(0, len(winners)), winners)
plt.xlabel("Generations")
plt.ylabel("Optimization Score")
plt.title("Finding Rosenbrock Root with 2^255 combinations")
plt.show()