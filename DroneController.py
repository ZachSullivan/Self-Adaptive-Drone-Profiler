import airsim
import py_trees
import functools # Needed for debugging/printing BT
import time

from Behaviors.FlyToBBTargetsAction import FlyToBBTargetsAction
from Behaviors.TakeoffAction import TakeoffAction
from Behaviors.LandAction import LandAction
from Blackboard.BlackboardManager import BlackboardManager


class DroneController():
    
    def __init__(self, takeoff_vel, flight_vel, tick_rate=0.5) -> None:
        
        # Take off and flight behaviors must have set desired velocities
        self.takeoff_vel = takeoff_vel
        self.flight_vel = flight_vel

        # Rate at which the BT should repeatedly tick, units in seconds
        self.tick_rate = tick_rate

        # Amount of energy consumed by the BT controller in simulation, units in Watts
        self.__total_energy = 0

        # Total mission time in seconds
        self.__mission_time = 0

        # Create a new blackboard through the blackboard manager
        # Manager is tasked with creating/returning blackboards, registering new keys within that blackboard
        self.blackboard_manager = BlackboardManager(name="Airsim")
        self.blackboard = self.blackboard_manager.getBlackboard()

        # A blackboard key is needed to store the Airsim client information
        self.blackboard_manager.registerKey(key="client") # defaults with read/write access
        self.blackboard_manager.registerKey(key="drone/waypoints") # defaults with read/write access
        self.blackboard_manager.registerKey(key="drone/height") # defaults with read/write access
        self.blackboard_manager.registerKey(key="drone/landed_state") # defaults with read/write access
        self.blackboard_manager.registerKey(key="terminate_bt")

        # Initalize connection to the Airim UE server
        # NOTE: the UE Blocks environment MUST be running before executing this drone controller.
        self.blackboard.client = airsim.MultirotorClient()
        self.blackboard.client.confirmConnection()
        self.blackboard.client.enableApiControl(True)
        self.blackboard.client.armDisarm(True)
        # Informs the BT update cycle when to terminate the BT loop
        # Value modified within the BT
        self.blackboard.terminate_bt = False

        self.blackboard.drone.height = 0
        self.blackboard.drone.landed_state = True

        # Initalize the mission waypoint targets
        self.blackboard.drone.waypoints = [
            airsim.Vector3r(0,0,-5), 
            airsim.Vector3r(10,0,-5), 
            #airsim.Vector3r(-10,0,-5),
            #airsim.Vector3r(-10,-10,-5),
            #airsim.Vector3r(10,-10,-5),
        ]
    
    # Debug function to visualize BT in console
    def __post_tick_handler(self, snapshot_visitor, behaviour_tree):
        print(
            py_trees.display.unicode_tree(
                behaviour_tree.root,
                visited=snapshot_visitor.visited,
                previously_visited=snapshot_visitor.visited
            )
        )

    # User defined Behavior Tree is defined and linked together here
    def __create_BT(self):
        # Create behavior tree sequences
        root = py_trees.composites.Sequence("Root Sequence")
        flight_sequence = py_trees.composites.Sequence("Flight Sequence") # Consists of takeoff and fly to waypoint behaviors
        land_sequence = py_trees.composites.Sequence("Land Sequence") # Consists of land, and check for sim end behavior
        
        # Create behavior tree behavior nodes
        takeoff = TakeoffAction("Take Off", velocity=(self.takeoff_vel*-1), targetAltitude=5)
        fly_to_target = FlyToBBTargetsAction(waypoints=self.blackboard.drone.waypoints, velocity=self.flight_vel)
        land = LandAction()

        # TODO: need to add a behavior that terminates BT

        # Construct the BT by linking the created nodes and sequences
        flight_sequence.add_children([takeoff, fly_to_target])
        land_sequence.add_children([land]) # TODO: need to append termination behavior node
        root.add_children([flight_sequence, land_sequence])

        # Establish the root of the BT
        behavior_tree = py_trees.trees.BehaviourTree(root=root)

        snapshot_visitor = py_trees.visitors.SnapshotVisitor()
        behavior_tree.add_post_tick_handler(
            functools.partial(self.__post_tick_handler,
                              snapshot_visitor))
        behavior_tree.visitors.append(snapshot_visitor)

        return behavior_tree

    # Return the velocity of the drone as a scalar
    def get_drone_velocity(self):
        multirotorStates = self.blackboard.client.getMultirotorState()
        return (multirotorStates.kinematics_estimated.linear_velocity.get_length())

    # Return a list of thrusts from each of the drone's rotors
    def get_rotor_thrusts(self):
        thrusts = []
        rotors = self.blackboard.client.getRotorStates().rotors
        for rotor in rotors:
            thrusts.append(rotor["thrust"])
        return thrusts

    # Return the total thrust generated by the drone
    def get_drone_thrust(self):
        return sum(self.get_rotor_thrusts())

    def __set_mission_time(self, elapsed_time):
        self.__mission_time = elapsed_time

    def get_mission_time(self):
        return self.__mission_time

    # Returns intantaneous energy generated from product of instant thrust and instant velocity
    def __energy_from_thrust(self, thrust, velocity):
        return (thrust*velocity)

    def __set_total_energy(self, energy):
        self.__total_energy = energy

    def get_total_energy(self):
        return self.__total_energy

    # Executes the Drone's BT logic through contious ticks, terminates upon BT request
    def update(self):

        bt = self.__create_BT()

        start_time = time.perf_counter()
        energy_measurements = []

        # Repeatedly tick the BT until termination call at a default rate of 500ms
        while self.blackboard.terminate_bt == False:
            bt.tick()

            energy_measurements.append(
                self.__energy_from_thrust(
                    self.get_drone_thrust(),
                    self.get_drone_velocity()
                )
            )
            
            time.sleep(self.tick_rate)
        
        elapsed_time = time.perf_counter() - start_time
        self.__set_mission_time(elapsed_time)
        self.__set_total_energy(sum(energy_measurements))