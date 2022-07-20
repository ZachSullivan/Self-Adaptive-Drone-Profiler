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

import airsim
import os
import py_trees
import time


class TakeoffAction(py_trees.behaviour.Behaviour):

    def __init__(self, name="Hover"):
        super(TakeoffAction, self).__init__(name)
        #blackboard = py_trees.blackboard.Client(name="Airsim")
        blackboard.register_key(key="client", access=py_trees.common.Access.READ)
        blackboard.register_key(key="z_axis", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="z_axis", access=py_trees.common.Access.READ)

        self.isComplete = False
        self.runningStatus = False
        self.client = blackboard.client
 
    def initalise(self):
        if self.isComplete == False:
            self.runningStatus = False
            print("initalising..")
        
    def update(self):

        print(self.runningStatus)


        # TODO: - z axis means up??? this needs to be fixed... check simGetVehiclePose
        blackboard.z_axis = self.client.simGetVehiclePose().position.z_val
        print("Drone's Z axis: " + str(blackboard.z_axis))
        
        if self.runningStatus == True:
            new_status = py_trees.common.Status.RUNNING
        else:
            #self.client.takeoffAsync()

            self.client.moveToZAsync(-4, 5)
            new_status = py_trees.common.Status.RUNNING
            self.runningStatus = True
        
        if round(blackboard.z_axis) == -4 or self.isComplete == True:
            print("Successfuly Taken Off!")
            new_status = py_trees.common.Status.SUCCESS
            self.isComplete = True

        return new_status

class FlyTowardsAction(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__()
        self.counter = 0
    def initalise(self):
        #self.counter = 0
        print("initalising..")

    def update(self):
        status = py_trees.common.Status.RUNNING
        self.counter += 1
        print("updating...")

        if self.counter == 10:
            status = py_trees.common.Status.SUCCESS

        return status

# Initalize and store Airsim client info
blackboard = py_trees.blackboard.Client(name="Airsim")
blackboard.register_key(key="client", access=py_trees.common.Access.WRITE)

blackboard.client = airsim.MultirotorClient()
blackboard.client.confirmConnection()
blackboard.client.enableApiControl(True)
blackboard.client.armDisarm(True)
#print(py_trees.display.unicode_blackboard())

root = py_trees.composites.Sequence("Sequence")
takeoff = TakeoffAction()
flytowards = FlyTowardsAction()
root.add_children([takeoff, flytowards])

behavior_tree = py_trees.trees.BehaviourTree(root=root)


try:
    for i in range(0, 100):
        behavior_tree.tick()
        time.sleep(0.5)
    print("\n")
except KeyboardInterrupt:
    pass
