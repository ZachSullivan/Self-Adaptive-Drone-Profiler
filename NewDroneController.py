import airsim
import py_trees
import time


from GAv5 import GA

from Behaviors.FlyToBBTargetsAction import FlyToBBTargetsAction
from Behaviors.TakeoffAction import TakeoffAction
from Behaviors.Terminate import Terminate

from Blackboard.BlackboardManager import BlackboardManager

# Drone Controller contains three primary submethods, Create BT and update.
# Create BT takes several arguments which define the behavior parameters of the BT. for instance, what waypoints to travel to, take off velocities, in flight velocities, etc.
# Update takes a single argument, a BT to execute.
# Finally, simuate_bt takes a single argument, and calls create_bt, and update, and returns the corresponding fitness of that simulated BT

class NewDroneController():

    def __init__(self) -> None:

        print("initalized")

        #Amount of energy consumed by the BT controller in simulation, units in Watts
        self.__total_energy = 0

        # Total mission time in seconds
        self.__mission_time = 0

        # Define the contents of the drone controller's BT blackboard

        """self.blackboard = py_trees.blackboard.Client(name="Airsim")
        self.blackboard.register_key(key="client", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="client", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="drone/waypoints", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="drone/waypoints", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="drone/height", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="drone/height", access=py_trees.common.Access.READ)
        
        self.blackboard.register_key(key="sim/status", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="sim/status", access=py_trees.common.Access.READ)

        self.blackboard.client = airsim.MultirotorClient()
        self.blackboard.client.confirmConnection()
        self.blackboard.client.enableApiControl(True)
        self.blackboard.client.armDisarm(True)"""

        self.blackboard_manager = BlackboardManager(name="Airsim")
        self.blackboard = self.blackboard_manager.getBlackboard()

        self.blackboard_manager.registerKey("client")
        self.blackboard_manager.registerKey(key="drone/waypoints")
        self.blackboard_manager.registerKey(key="drone/height")
        self.blackboard_manager.registerKey(key="sim/status")
        
        
        self.blackboard.client = airsim.MultirotorClient()
        self.blackboard.client.confirmConnection()
        self.blackboard.client.enableApiControl(True)
        self.blackboard.client.armDisarm(True)
        
        self.terminate_bt = False

    def __set_mission_time(self, t):
        self.__mission_time = t

    def __set_total_energy(self, e):
        self.__total_energy = e

    def get_total_energy(self):
       return self.__total_energy

    def get_mission_time(self):
        return self.__mission_time

    def create_BT(self, takeoff_vel=1, waypoints=[], flight_vel=1):

        root = py_trees.composites.Sequence("Root Sequence")
        flight_sequence = py_trees.composites.Sequence("Flight Sequence")

        
        # Create behavior tree behavior nodes
        takeoff = TakeoffAction("Take Off", velocity=(takeoff_vel*-1), targetAltitude=5)
        fly_to_target = FlyToBBTargetsAction(waypoints=waypoints, velocity=flight_vel)
        terminate = Terminate()

        # Construct the BT by linking the created nodes and sequences
        flight_sequence.add_children([takeoff, fly_to_target])
        root.add_children([flight_sequence, terminate])

        # Establish the root of the BT
        behavior_tree = py_trees.trees.BehaviourTree(root=root)

        return behavior_tree

    def update(self, bt):
        self.blackboard.sim.status = py_trees.common.Status.INVALID
        

        start_time = time.perf_counter()
        energy_measurements = []

        # Repeatedly tick the BT until termination call at a default rate of 500ms
        while self.terminate_bt == False:
            thrusts = []
            elapsed_time = time.perf_counter() - start_time
            
            bt.tick()


            # Return a list of thrusts from each of the drone's rotors
            rotors = self.blackboard.client.getRotorStates().rotors
            for rotor in rotors:
                thrusts.append(rotor["thrust"])

            # Return the total thrust generated by the drone's rotors at the current tick
            thrust = sum(thrusts)

            # Return the velocity of the drone at that given tick
            multirotorStates = self.blackboard.client.getMultirotorState()
            velocity = multirotorStates.kinematics_estimated.linear_velocity.get_length()

            energy_measurements.append((thrust*velocity))
            
            if self.blackboard.sim.status == py_trees.common.Status.SUCCESS:
                self.terminate_bt = True

            time.sleep(0.5)
        
        #elapsed_time = time.perf_counter() - start_time
        self.__set_mission_time(elapsed_time)
        self.__set_total_energy(sum(energy_measurements))

def fitness_function(params):
    print("\n\n\nNEW FITNESS FUNCTION")

    takeoff_vel = params[0]
    flight_vel = params[1]
    waypoints = [airsim.Vector3r(0,0,-5), airsim.Vector3r(10,0,-5)]

    drone = NewDroneController()
    bt = drone.create_BT(takeoff_vel, waypoints, flight_vel)
    drone.update(bt)

    

    return (drone.get_total_energy() + drone.get_mission_time())

ga = GA(fitness_function, fitness_shape=[2,10.5,2,3], pop_size=10, k=3, gen_count=5, mu=0.05)
ga.initialize()
ga.run()