
from operator import contains
import random
from random import randint
import numpy as np
from DroneController import DroneController

class GeneticAlgorithm():
   

    # Algorithm steps:
    """
    1. Start by computing an inital population. This would presumably be a population of randomized arguments for each behavior in the BT.
    ... such as, randomized take off velocities, randomized breaking velocity, TODO: Need to identify exactly what arguments would be randomized.
    2. Establish a while loop that continually iterates until a termination condition is reached, this ends the GA
    2.1 Generate scores for each indiviual in the population of params
    2.2 select which scored individuals within the current popualation should be repopulated.
    2.3 Produce offspring from the selected individuals by crossing over
    2.4 Select with a given probability a selection of offspring and mutate
    2.5 repeat the loop
    3. Once loop termination logic is reached, return the best fit individual
    """

    """ 
    V1: GA is optimizing the take off and waypoint flight velocities with respect to minizing energy consumed during mission AND minimizing mission flight time
    """

    def __init__(self, pop_n=100, mu=0.03, min_vel=1,max_vel=10) -> None:
    
        self.pop_n = pop_n
        self.__pop = []
        self.__mu = mu # Probability for a bit to mutate
        self.__score_table = dict() # Lookup table that records bistrings as keys and their simulated score as value
        self.__max_vel = max_vel # maximum velocity which the GA can use to initialize an individual param
        self.__min_vel = min_vel  # Minimum velocity for GA initalize 

    # Takes a string of integers and produces a list of ints
    def __binary_string_to_binary_list(self, string):
        string = list(string)
        i_list = list()
        for s in string:
            i_list.append(int(s))
        return i_list

    # Takes an encoded bitstring, and returns the decoded params stored in a list
    def __decode_bitstring_to_params(self, bit_string=""):
        bit_string_len = len(bit_string)
        p1 = int(bit_string[:bit_string_len//2], 2)
        p2 = int(bit_string[bit_string_len//2:], 2)

        return [p1,p2]

    # Takes an encoded bitlist, and returns the decoded params stored in a list
    def __decode_bitlist_to_params(self, bitlist=[]):

        cross_point = int(len(bitlist)/2)
        
        p1 = int("".join(str(x) for x in bitlist[:cross_point]), 2)
        p2 = int("".join(str(x) for x in bitlist[cross_point:]), 2)

        return [p1, p2]

    # Generate a bitlist from a list of concatenated elements
    #def __generate_bitstring(self, int_list=[]):
    def __generate_bitlist(self, int_list=[]):
        bit_string = ""
        for i in int_list:
            b = format(i, "04b") # Format the int value to binary, keeping leading 4 0s
            bit_string+=str(b)
        bit_list = self.__binary_string_to_binary_list(bit_string)
        return bit_list

    def __bitlist_to_bitstring(self, bitlist):
        return ("".join(str(x) for x in bitlist))

    # Takes a list of child bitlists and inserts them into the population
    def __insert_offspring(self, children):
        for child in children:
            self.__pop.append(child)

    def set_pop(self, pop):
        self.__pop = pop

    # Tournament Selection Algorithm
    # Take k number of individuals from the population, compete against each other. 
    # k is our selection pressure and directly correlates to rate of convergence, Higher k = higher rate of convergence 
    # Winner from k individuals is returned as the selected individual from the tournament.
    # Repeat for all individuals in the population have competed
    # k cannot be larger than the pop size
    # Takes scored individuals a list of tuples 
    # Returns winners and their scores as a list of tuples
    def __tournament_selection(self, k):
        
        if k > self.pop_n:
            raise Exception("Selection pressure K is larger than pop size")
        # Order the population by fitness
        #scores = sorted(scores, lambda x: x[1])

        best_score = None
        best_individual = None
        for i in range(k):
            #selected = scores[randint(0, self.pop_n-1)]
            rnd_idx = randint(0, len(self.__pop)-1)
            bit_list = self.__pop[rnd_idx]
           
            # Checks a lookup table first, if that key (bitstring) has a value (score) already set
            # .. if not simulate, score and record in lookup table, then perform best fit check
            drone_param = self.__decode_bitlist_to_params(bit_list)
            bit_string = self.__bitlist_to_bitstring(bit_list)

            if bit_string not in self.__score_table.keys():
                print("BITSTRING: "+ bit_string+" NOT YET SIMULATED, SCORING...")
                score = self.__simulate_drone(drone_param)
                print("SCORED, ADDING TO LOOKUP TABLE")
                self.__score_table[bit_string] = score
            else:
                print("BITSTRING ALREADY SIMULATED, ADDING RECORDED SCORE")
                score = self.__score_table[bit_string]

            if best_score == None or score < best_score:
                best_score = score
                best_individual = bit_list
        
        print("Tournament Winner: " + str(best_individual)+ " Score: " + str(best_score))

        return best_individual

    # Takes a list of parameters which the drone should simulate, returns its score
    # Parameter list is passed to the drone controller as its constructor arugments
    def __simulate_drone(self, params):
        if params == None or len(params) == 0:
            raise Exception("No drone behavior parameters provided")

        drone = DroneController(takeoff_vel=params[0], flight_vel=params[1], epochs=1, timeout=60)
        drone.update()

        # At the moment a score is the sum of its consumed energy and time taken
        # TODO: explore alternative scoring equations
        return (drone.get_total_energy() + drone.get_mission_time())

    def __crossover(self, parent1, parent2):
        
        cross_point = randint(0, len(parent1)-1)

        p1 = self.__binary_string_to_binary_list(parent1)
        p2 = self.__binary_string_to_binary_list(parent2)

        cross_p1 = p1[:cross_point]
        cross_p2 = p2[cross_point:]

        child1 = (cross_p1 + cross_p2)
        child1 = self.__mutate(child1)

        cross_p1 = p1[cross_point:]
        cross_p2 = p2[:cross_point]

        child2 = (cross_p2 + cross_p1)
        child2 = self.__mutate(child2)

        return (child1, child2)

    # Takes a bitlist and randomly flips with prob mu each of its bits
    def __mutate(self, bitlist):
        #binary = self.__binary_string_to_binary_list(bitstring)
        binary = bitlist
        for i, bit in enumerate(binary):
            if random.random() < self.__mu:
                binary[i] = int(bit) ^ 1
        print("BINARY CHECK")
        #params = self.__decode_bitlist_to_params(binary)
        #bitstring = self.__generate_bitstring(params)
        #return bitstring
        return binary

    # Takes population size as argument, returns a list of that number of randomzied individuals 
    # When randomizing the population, need to make sure that no two individuals are the same
    # Note self is required for accessing private functions in the same class
    def init_pop(self):
        pop = []
        for i in range(self.pop_n):
            
            # Generate two randomized param values between min/max vel ranges, combine them into a single encoded bit string
            bit_list = self.__generate_bitlist([randint(self.__min_vel, self.__max_vel) for x in range(2)]) #[randint(self.min_vel, self.max_vel), randint(self.min_vel, self.max_vel)])
            
            # Check if this bit string already exists in the population. 
            while bit_list in pop:
                # If it does exist, generate a new bit string
                print("BIT STRING ALREADY IN POP, GENERATING A NEW BIT STRING")
                bit_list = self.__generate_bitlist([randint(self.__min_vel, self.__max_vel) for x in range(2)])

            pop.append(bit_list)    

        return pop

    # Loop that continually iterates for a given number of epochs (default 10), then ends the GA
    def update(self, epochs=1):
        for e in range(epochs):
            # 2.1 select which individuals within the current popualation should be repopulated.
            # If the selected has not been scored, simuate in airsim and score
            parent1 = self.__tournament_selection(k=self.pop_n-1)
            parent2 = self.__tournament_selection(k=self.pop_n-1)
            print("POP: " + str(self.__pop))
            print("Tournament Winners: " + str(parent1) + " and: " + str(parent2))

            # 2.2 Produce offspring from the selected individuals through single point crossover
            # Select a crossover point in the bitstring, as a random value between index 0 and len of bitstring - 1
            # TODO: package this crossover as a function

            children = self.__crossover(parent1, parent2)
            self.__insert_offspring(children)

            # 2.3 Select with a given probability a selection of offspring and mutate
            # NOTE: too high of a mutation probability will devolve the GA into a random search
            # 2.3.1 Randomly select via index child(0, N-1), with given mutation prob flip the selected bit
            # Each given bit in the childs bit string has a mu probability to mutate

ga = GeneticAlgorithm(10, 0.03, 1, 10)

# 1. Start by computing an inital population. This would presumably be a population of randomized arguments for each behavior in the BT.
ga_population = ga.init_pop()
ga.set_pop(ga_population)

# 2. Establish a loop that continually iterates until a termination condition is reached, this ends the GA
ga.update(epochs=4)

# Termination condition is the number of desired iterations/epochs 1 2 3 4 5 6
