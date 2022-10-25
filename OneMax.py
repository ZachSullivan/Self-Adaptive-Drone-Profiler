from GAv3 import GA
import matplotlib.pyplot as plt

def fitness_function(x):
   return -sum(x)

ga = GA(fitness_function=fitness_function, bounds=[0,0], bit_size=20, pop_size=100, mu=0.05, gens=100)

ga.initalize()
best_params, best_fitness = ga.run()
print("> Best Solution:{0} W/ score: {1}\n".format(
                best_params, best_fitness))

winners = ga.get_winners()
fig, ax = plt.subplots()
plt.scatter(range(0, len(winners)), winners)
plt.xlabel("Generations")
plt.ylabel("Optimization Score")
plt.title("Finding OneMax optimal")
plt.show()