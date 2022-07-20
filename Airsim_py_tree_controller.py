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


class Action(py_trees.behaviour.Behaviour):

    def __init__(self, name="Action"):
        super(Action, self).__init__(name)
        self.percentageComplete = 0
        self.drone_data = None

    def setup(self):
        # Connect to the airsim client
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection() # repeatedly check client connection every 1s
        self.client.enableApiControl(True) # Enables autonmous api control instead of manual human control
        self.client.armDisarm(True)
        self.drone_data = self.client.getDistanceSensorData("Distance", "TestDrone")

    def initalise(self):
        self.percentageComplete = 0
        
    def update(self):
        new_status = py_trees.common.Status.RUNNING
        if self.percentageComplete == 100:
            new_status = py_trees.common.Status.SUCCESS

        if new_status != py_trees.common.Status.SUCCESS:
            self.percentageComplete += 10
            print(self.percentageComplete)
            print("drone data: " + str(self.drone_data))

        return new_status


action = Action()
action.setup()

try:
    for i in range(0, 10):
        action.tick_once()
        time.sleep(0.5)
    print("\n")
except KeyboardInterrupt:
    pass
