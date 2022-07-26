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

from types import NoneType
import airsim
import os
import py_trees
import time


class zAxisAction(py_trees.behaviour.Behaviour):

    def __init__(self, name="Hover", velocity=0, targetAltitude=5):
        super(zAxisAction, self).__init__(name)

        self.name = name
        self.isComplete = False
        self.runningStatus = False
        self.target_altitude = targetAltitude
        self.duration = blackboard.drone.API_timeout
        self.api_start_time = time.perf_counter()
        self.velocity = velocity

    def initialise(self):
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
            """# Check if the API call timed out
            elapsed_time = (time.perf_counter() - self.api_start_time)
            print("Elapsed Time: " + str(elapsed_time))
            if elapsed_time >= self.duration:
                new_status = py_trees.common.Status.FAILURE

            else:"""

            # If the behavior has not already been called, call it
            #if self.runningStatus == False:
            

            # Provide the drone with an upwards velocity impulse, along z axis, for 3 seconds
            blackboard.client.moveByVelocityAsync(0, 0, self.velocity, 1)     
            """if self.runningStatus == False:
                print("Taking Off...")
                blackboard.client.takeoffAsync()
                self.runningStatus = True"""
            # If the behavior is running, poll the drone's height sensor
            # else:
            #print("take off already started, polling height")
             
            


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

class FlyTowardsAction(py_trees.behaviour.Behaviour):
    def __init__(self, duration):
        super().__init__()
        self.api_start_time = time.perf_counter()
        self.duration = duration
        self.isComplete = False

    def initialise(self):
        if self.isComplete == True:
            return py_trees.common.Status.SUCCESS

    def update(self):
        
        elapsed_time = (time.perf_counter() - self.api_start_time)
        if elapsed_time >= self.duration:
            print("fly forward timelimit reached")
            self.isComplete = True
            return py_trees.common.Status.SUCCESS          
         
        print("Executing fly forward behavior...")
        blackboard.client.moveByVelocityAsync(2, 0, 0, 1)     

        return py_trees.common.Status.RUNNING

# Initalize and store Airsim client info
blackboard = py_trees.blackboard.Client(name="Airsim")
blackboard.register_key(key="client", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="client", access=py_trees.common.Access.READ)

# Initalize and store drone sensor info
blackboard.register_key(key="drone/height", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="drone/height", access=py_trees.common.Access.READ)

# All Airsim API movement calls MUST be provided a duration value
blackboard.register_key(key="drone/API_timeout", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="drone/API_timeout", access=py_trees.common.Access.READ)

blackboard.client = airsim.MultirotorClient()
blackboard.client.confirmConnection()
blackboard.client.enableApiControl(True)
blackboard.client.armDisarm(True)
blackboard.drone.API_timeout = 10000   # Timeout any movement API calls after 10 seconds

print(py_trees.display.unicode_blackboard())

# Create behavior tree nodes and link the tree together
root = py_trees.composites.Sequence("Sequence1")
sequence = py_trees.composites.Sequence("Sequence2")
takeoff = zAxisAction("Take Off", -2)
flytowards = FlyTowardsAction(4)
land = zAxisAction("Land", 2, 0)
sequence.add_children([takeoff, flytowards])
root.add_children([sequence, land])

behavior_tree = py_trees.trees.BehaviourTree(root=root)

# Iterate the tree
try:
    for i in range(0, 25):
        behavior_tree.tick()
        time.sleep(0.5)
    print("\n")
except KeyboardInterrupt:
    pass
