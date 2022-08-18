
from random import randint

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

    def __init__(self, pop_n=100, min_vel=1,max_vel=10) -> None:
    
        self.pop_n = pop_n
        self.__pop = []
        self.__max_vel = max_vel # maximum velocity which the GA can use to initialize an individual param
        self.__min_vel = min_vel  # Minimum velocity for GA initalize 

    # Takes an encoded bitstring, and returns the decoded params stored in a list
    def __bitstring_to_list(self, bit_string=""):
        bit_string_len = len(bit_string)
        p1 = int(bit_string[:bit_string_len//2], 2)
        p2 = int(bit_string[bit_string_len//2:], 2)

        return [p1,p2]

    # Generate a bitstring from a list of concatenated elements
    def __generate_bitstring(self, int_list=[]):
        bit_string = ""
        for i in int_list:
            b = format(i, "04b") # Format the int value to binary, keeping leading 4 0s
            bit_string+=str(b)
        return bit_string

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
    def __tournament_selection(self, k, scores=[]):
        
        if k > self.pop_n:
            raise Exception("Selection pressure K is larger than pop size")

        # Copy the population into a list of tournament contenders
        contenders = scores
        
        # List of active competitors in the tournament.
        warriors = []
        for i in range(k):
            # Randomly select an individual from the list of contenders
            # .. add them to the list of warriors, Pop the selected from the list of contenders
            warriors.append(contenders.pop(randint(0, len(contenders)-1)))
        
        # Pit the warriors against each other
        highest_fitness = None
        for w in warriors:
            # Selecting those with the LOWEST score
            # TODO: This assumes SCORE and FITNESS are the same.. perhaps not.. 

            # IDEA: instead of scoring ALL individuals and THEN selecting, instead select, then score, then return winner...
            # .. everytime I compute a score, save it in a lookup table that matches bitstring to score. saving compuation
            if highest_fitness is None or w[1] < highest_fitness[1]:
                highest_fitness = w
        return highest_fitness
    # Takes population size as argument, returns a list of that number of randomzied individuals 
    # When randomizing the population, need to make sure that no two individuals are the same
    # Note self is required for accessing private functions in the same class
    def init_pop(self, pop_n):
        pop = []
        for i in range(pop_n):
            
            # Generate two randomized param values between min/max vel ranges, combine them into a single encoded bit string
            bit_string = self.__generate_bitstring([randint(self.__min_vel, self.__max_vel) for x in range(2)]) #[randint(self.min_vel, self.max_vel), randint(self.min_vel, self.max_vel)])
            
            # Check if this bit string already exists in the population. 
            while bit_string in pop:
                # If it does exist, generate a new bit string
                print("BIT STRING ALREADY IN POP, GENERATING A NEW BIT STRING")
                bit_string = self.__generate_bitstring([randint(self.__min_vel, self.__max_vel) for x in range(2)])
            
            # Debug
            print("DECODED: "+ str(self.__bitstring_to_list(bit_string=bit_string)))

            pop.append(bit_string)    

        return pop

    # Loop that continually iterates for a given number of epochs (default 10), then ends the GA
    def update(self, epochs=1):
        for e in range(epochs):
            scores = [] # list of Tuples, where each tuple contains the individual and its score
            # 2.1 Generate scores for each indiviual in the population of params
            for bit_string in self.__pop:

                params = self.__bitstring_to_list(bit_string)

                print(params)
                drone = DroneController(takeoff_vel=params[0], flight_vel=params[1], epochs=1)
                drone.update()

                # At the moment a score is the sum of its consumed energy and time taken
                # TODO: explore alternative scoring equations
                score = (drone.get_total_energy() + drone.get_mission_time())
                scores.append((bit_string, score))
            
            print("Scores: " + str(scores))
               
            # 2.2 select which scored individuals within the current popualation should be repopulated.
            winner = self.__tournament_selection(k=2, scores=scores)

            print("Tournament Winner: " + str(winner))
            # 2.3 Produce offspring from the selected individuals by crossing over


            # 2.4 Select with a given probability a selection of offspring and mutate


ga = GeneticAlgorithm(100, 1, 10)

# 1. Start by computing an inital population. This would presumably be a population of randomized arguments for each behavior in the BT.
ga_population = ga.init_pop(pop_n=3)
ga.set_pop(ga_population)

# 2. Establish a loop that continually iterates until a termination condition is reached, this ends the GA
ga.update(epochs=1)

# Termination condition is the number of desired iterations/epochs
