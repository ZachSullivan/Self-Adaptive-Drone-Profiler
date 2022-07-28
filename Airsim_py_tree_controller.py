"""
V2
fly forward
check if I have reached a wall
If a wall is approaching, stop
rotate in increments of 5 degrees
check if a wall is infront of me and blocking me
fly forward and repeat

V1
Have I taken off?
n: take off and hover
y: Do I have a target waypoint to move to?
n: Obtain nearest waypoint
y: Sequence
    1: Move to that waypoint
    2
Am I moving to a waypoint
"""

import functools
from types import NoneType
import airsim
import os
import py_trees
import time
from Behaviors.FlyToBBTargetsAction import FlyToBBTargetsAction
from Behaviors.GetBBTarget import GetBBTarget
from Blackboard.BlackboardManager import BlackboardManager

class TakeoffAction(py_trees.behaviour.Behaviour):

    def __init__(self, name="Takeoff", velocity=0, targetAltitude=5):
        super(TakeoffAction, self).__init__(name)

        self.name = name
        self.isComplete = False
        self.runningStatus = False
        self.target_altitude = targetAltitude
        self.duration = blackboard.drone.API_timeout
        self.api_start_time = time.perf_counter()
        self.velocity = velocity

    def initialise(self):
        blackboard.drone.landed_state = False
        if self.isComplete == False:
            self.api_start_time = time.perf_counter()
            self.runningStatus = False
            print(self.name + " initalising..")
        
    def update(self):

        blackboard.drone.height = blackboard.client.getDistanceSensorData(distance_sensor_name="Height").distance

        print(blackboard.drone.height)



        if round(blackboard.drone.height) == self.target_altitude:# or self.isComplete == True:
                    
            new_status = py_trees.common.Status.SUCCESS
            self.isComplete = True

        # Check if the behavior has completed
        if self.isComplete == True:
            print(self.name + " Successfull")
            new_status = py_trees.common.Status.SUCCESS
        
        # Behavior has either not yet started or is currently running
        else:
            new_status = py_trees.common.Status.RUNNING
            # Provide the drone with an upwards velocity impulse, along z axis, for 1 seconds
            blackboard.client.moveByVelocityAsync(0, 0, self.velocity, 1)     

        return new_status

class HoverAction(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__()
        self.isComplete = False

    def initialise(self):

        print("landing initalising..")

    def update(self):
      
        print("Landing...")

        
        status = py_trees.common.Status.RUNNING
        blackboard.client.landAsync()

        return status

class LandAction(py_trees.behaviour.Behaviour):
    def __init__(self, velocity = 2):
        super().__init__()
        self.isComplete = False
        self.velocity = velocity

    def initialise(self):
        print("landing initalising..")
        if blackboard.drone.landed_state == True:
            print("Already Landed!")
            return py_trees.common.Status.FAILURE


    def update(self):
        blackboard.drone.height = blackboard.client.getDistanceSensorData(distance_sensor_name="Height").distance

        print(round(blackboard.drone.height))

        # Check if the behavior has completed
        if round(blackboard.drone.height) == 0:
            print("Landing Successful!")
            blackboard.drone.landed_state = True  
            return py_trees.common.Status.SUCCESS

        # Behavior has either not yet started or is currently running
        else:
            print("Landing...")
            new_status = py_trees.common.Status.RUNNING
            # Provide the drone with an upwards velocity impulse, along z axis, for 1 seconds
            blackboard.client.moveByVelocityAsync(0, 0, self.velocity, 1)     

        return new_status


"""class FlyTowardsAction(py_trees.behaviour.Behaviour):
    def __init__(self, duration=None, waypoints=[]):
        super().__init__()
        self.api_start_time = time.perf_counter()
        self.duration = duration
        self.isComplete = False
        self.waypoints = waypoints
        self.waypoint_index = 0
        self.target = None

    def initialise(self):
        if len(self.waypoints) > 0:
            print("INITALIZSING FLY TO WAYPOINT TARGET")
            if self.waypoint_index < len(self.waypoints):
                self.target = self.waypoints[self.waypoint_index]
                #self.waypoint_index += 1
            else:
                return py_trees.common.Status.SUCCESS

    def update(self):
        
        #drone_pos = blackboard.client.getMultirotorState().getPosition()
        drone_pos = blackboard.client.simGetVehiclePose().position
        

        if self.duration is not None:
            elapsed_time = (time.perf_counter() - self.api_start_time)
            if elapsed_time >= self.duration:
                print("fly forward timelimit reached")
                self.isComplete = True
                return py_trees.common.Status.FAILURE          
        
        if self.target != None:
            print(round(self.target.x_val - drone_pos.x_val))
            
            if round(self.target.x_val - drone_pos.x_val) <= 1 and round(self.target.y_val - drone_pos.y_val) <= 1:
                print("Destination arrived")
                # check if there are any other destinations to visit
                if len(self.waypoints) > 0:
                    print("Checking for next waypoint..")
                    if self.waypoint_index < len(self.waypoints):
                        print("New Waypoint found!")
                        self.target = self.waypoints[self.waypoint_index]
                        self.waypoint_index += 1
                        print("Executing fly towards target behavior...")
                        blackboard.client.moveToPositionAsync(self.target.x_val, self.target.y_val, self.target.z_val, 2)
                        return py_trees.common.Status.RUNNING
 
                    else:
                        print("No New Waypoint found, ENDING")
                        self.isComplete = True
                        return py_trees.common.Status.SUCCESS


                
                #return py_trees.common.Status.SUCCESS
            else:
                print("Executing fly towards target behavior...")
                blackboard.client.moveToPositionAsync(self.target.x_val, self.target.y_val, self.target.z_val, 2)
        else:
            print("Executing fly forward behavior...")
            blackboard.client.moveByVelocityAsync(2, 0, 0, 1)     

        return py_trees.common.Status.RUNNING"""

# Initalize and store Airsim client info
airsimBlackboardManager = BlackboardManager(name="Airsim")
airsimBlackboardManager.registerKey(key="client")
airsimBlackboardManager.registerKey(key="drone/height")
airsimBlackboardManager.registerKey(key="drone/waypoints")
airsimBlackboardManager.registerKey(key="drone/target")
airsimBlackboardManager.registerKey(key="drone/API_timeout")
airsimBlackboardManager.registerKey(key="drone/landed_state")
#blackboard = py_trees.blackboard.Client(name="Airsim")
#blackboard.register_key(key="client", access=py_trees.common.Access.WRITE)
#blackboard.register_key(key="client", access=py_trees.common.Access.READ)

# Initalize and store drone sensor info
#blackboard.register_key(key="drone/height", access=py_trees.common.Access.WRITE)
#blackboard.register_key(key="drone/height", access=py_trees.common.Access.READ)

# All Airsim API movement calls MUST be provided a duration value
#blackboard.register_key(key="drone/API_timeout", access=py_trees.common.Access.WRITE)
#blackboard.register_key(key="drone/API_timeout", access=py_trees.common.Access.READ)

# Initialize and store drone landed state
#blackboard.register_key(key="drone/landed_state", access=py_trees.common.Access.WRITE)
#blackboard.register_key(key="drone/landed_state", access=py_trees.common.Access.READ)

# Create a serise of waypoints visiable in simulation
waypoints = [
    airsim.Vector3r(10,0,-5), 
    airsim.Vector3r(-10,0,-5),
    airsim.Vector3r(-10,-10,-5),
    airsim.Vector3r(10,-10,-5),
]

blackboard = airsimBlackboardManager.getBlackboard()

blackboard.client = airsim.MultirotorClient()
blackboard.client.confirmConnection()
blackboard.client.enableApiControl(True)
blackboard.client.armDisarm(True)
blackboard.drone.API_timeout = 10000   # Timeout any movement API calls after 10 seconds
blackboard.drone.landed_state = True
blackboard.drone.waypoints = waypoints
blackboard.drone.target = None

print(py_trees.display.unicode_blackboard())

def post_tick_handler(snapshot_visitor, behaviour_tree):
    print(
        py_trees.display.unicode_tree(
            behaviour_tree.root,
            visited=snapshot_visitor.visited,
            previously_visited=snapshot_visitor.visited
        )
    )


blackboard.client.simPlotPoints(points=waypoints, size=25, is_persistent=True)

# Create behavior tree nodes
root = py_trees.composites.Sequence("Sequence1")
flightSequence = py_trees.composites.Sequence("Flight Sequence")
takeoff = TakeoffAction("Take Off", -2)

# Queries for a target location, flys to it
flyToBBTargets = FlyToBBTargetsAction(waypoints=blackboard.drone.waypoints)
land = LandAction()


# Construct the BT by linking the created nodes
flightSequence.add_children([takeoff, flyToBBTargets])
root.add_children([flightSequence, land])
behavior_tree = py_trees.trees.BehaviourTree(root=root)

snapshot_visitor = py_trees.visitors.SnapshotVisitor()
behavior_tree.add_post_tick_handler(
    functools.partial(post_tick_handler,
                      snapshot_visitor))
behavior_tree.visitors.append(snapshot_visitor)


# Iterate the tree
try:
    for i in range(0, 100):
        #print(py_trees.display.ascii_tree(root))
        behavior_tree.tick()
        time.sleep(0.5)
    print("\n")
except KeyboardInterrupt:
    pass

