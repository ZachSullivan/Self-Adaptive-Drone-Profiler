
import functools
from types import NoneType
import airsim
import os
import py_trees
import time
import numpy as np

# export the energy model data in csv format
import csv

import Waypoint_visualization

from Behaviors.FlyToBBTargetsAction import FlyToBBTargetsAction
from Behaviors.GetBBTarget import GetBBTarget
from Behaviors.TakeoffAction import TakeoffAction
from Behaviors.LandAction import LandAction
from Behaviors.SimEpochAction import SimEpochAction
from Blackboard.BlackboardManager import BlackboardManager

class Power4r():
    rotor_1 = 0.0
    rotor_2 = 0.0
    rotor_3 = 0.0
    rotor_4 = 0.0

    def __init__(self, rotor_1 = 0.0, rotor_2 = 0.0, rotor_3 = 0.0, rotor_4 = 0.0):
        self.rotor_1 = rotor_1
        self.rotor_2 = rotor_2
        self.rotor_3 = rotor_3
        self.rotor_4 = rotor_4

    def add(self, rotor_1, rotor_2, rotor_3, rotor_4):
        self.rotor_1 += rotor_1
        self.rotor_2 += rotor_2
        self.rotor_3 += rotor_3
        self.rotor_4 += rotor_4

    def __str__(self) -> str:
        return str([self.rotor_1, self.rotor_2, self.rotor_3, self.rotor_4])

# Initalize and store Airsim client info
airsimBlackboardManager = BlackboardManager(name="Airsim")
airsimBlackboardManager.registerKey(key="client")
airsimBlackboardManager.registerKey(key="sim/epoch_count")
airsimBlackboardManager.registerKey(key="sim/epoch_limit")
airsimBlackboardManager.registerKey(key="sim/status")
airsimBlackboardManager.registerKey(key="drone/height")
airsimBlackboardManager.registerKey(key="drone/waypoints")
airsimBlackboardManager.registerKey(key="drone/target")
airsimBlackboardManager.registerKey(key="drone/API_timeout")
airsimBlackboardManager.registerKey(key="drone/landed_state")
airsimBlackboardManager.registerKey(key="drone/rotors/power")

# Create a serise of waypoints visiable in simulation
waypoints = [
    airsim.Vector3r(0,0,-5), 
    airsim.Vector3r(10,0,-5), 
    #airsim.Vector3r(-10,0,-5),
    #airsim.Vector3r(-10,-10,-5),
    #airsim.Vector3r(10,-10,-5),
]

blackboard = airsimBlackboardManager.getBlackboard()

blackboard.client = airsim.MultirotorClient()
blackboard.client.confirmConnection()
blackboard.client.enableApiControl(True)
blackboard.client.armDisarm(True)
blackboard.sim.epoch_count = 0  
blackboard.sim.epoch_limit = 1  # the maximum number of simuation epochs that can be run. new epoch is recorded after each drone reset
blackboard.sim.status = py_trees.common.Status.INVALID
blackboard.drone.API_timeout = 10000   # Timeout any movement API calls after 10 seconds
blackboard.drone.landed_state = True
blackboard.drone.waypoints = waypoints
blackboard.drone.target = None
blackboard.drone.rotors.power = Power4r(0, 0, 0, 0)

print(py_trees.display.unicode_blackboard())

# Debug function to visualize BT in console
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
flightSequence = py_trees.composites.Sequence("Flight Sequence") # Consists of takeoff and fly to waypoint
takeoff = TakeoffAction("Take Off", velocity=-4, targetAltitude=5)

# Queries for a target location, flys to it
flyToBBTargets = FlyToBBTargetsAction(waypoints=blackboard.drone.waypoints, velocity=2)

landSequence = py_trees.composites.Sequence("Land Sequence") # Consists of land, and check for sim end behavior
land = LandAction(8)
updateSimEpoch = SimEpochAction()


# Construct the BT by linking the created nodes
flightSequence.add_children([takeoff, flyToBBTargets])
landSequence.add_children([land, updateSimEpoch])
root.add_children([flightSequence, landSequence])
behavior_tree = py_trees.trees.BehaviourTree(root=root)


# Debug to visualize BT in console
snapshot_visitor = py_trees.visitors.SnapshotVisitor()
behavior_tree.add_post_tick_handler(
    functools.partial(post_tick_handler,
                      snapshot_visitor))
behavior_tree.visitors.append(snapshot_visitor)

# Returns a list of each thrust generated from the four rotors
def getThrusts():
    thrusts = []
    rotors = blackboard.client.getRotorStates().rotors
    for rotor in rotors:
        thrusts.append(rotor["thrust"])
    return thrusts

def getCentroidThrust():
    rotorStates = blackboard.client.getRotorStates()
    rotors = rotorStates.rotors
    #rotors = getRotors()
    return sum(rotor["thrust"] for rotor in rotors)

# Compute a energy cost from thrust
def getPowerFromThrust():
    rotorStates = blackboard.client.getRotorStates()
    multirotorStates = blackboard.client.getMultirotorState()

    rotors = rotorStates.rotors
    vel_i = multirotorStates.kinematics_estimated.linear_velocity.get_length()
    #acc = multirotorStates.kinematics_estimated.linear_acceleration.get_length()

    #print(rotors)
    #print("instant Velocity: m/s " + str(vel_i))
    #print("acceleration: m/s^2 " + str(acc))
    #print("elapsed time: s " + str(time))

    #distance = (vel*time)

    #print("Distance travelled: m " + str(distance))
    thrust = 0
  
    for rotor in rotors:
        thrust += rotor["thrust"]
        # IDEA: need to sum the 4 thrust vectors to obtain a centroid thrust vector, THEN use the velocity and acceleration vectors as those are computed from the center of the drone

        # Compute watts as an instanteous measurement
        # Continuoyusly sum my computated watts in a given instance to produce a rate of work as Watt Hours (which is directly equivlent to joules, 1 watt second = 1 joule)
        # Note a sum of all 4 thrust vectors produces a singular thrust vector from the center of the drone

    #print("centroid thrust: N " + str(thrust))

    rotorPower = (thrust * vel_i)

    return rotorPower

# Total distance is the sum of distances i through n, with with integral distances computed halfway between vi and vi_star
def computeDistance(vi, t):
    return (vi*t)
 
start_time = time.perf_counter()
elapsed_time = 0
dronePower = 0

distances = []
distance_i = [] # Stores the instant distance computed at each BT tick
power_i = []
centroid_thrusts = []
four_thrusts = [] # multidimisional list of each thrust from the 4 rotors
times = []
vel_i = []

# Iterate the tree
try:

    while True:
    #while blackboard.client.sim_epochs < 2:
    #for i in range(0, 40):
        # Record elapsed mission time
        """
        # This should be a Conditional node and a behavior in the BT...
        # Check If the drone has landed
        if blackboard.drone.landed_state == True:
            print("RESETING DRONE")
            # Get the present pose of the drone
            pose = blackboard.client.simGetVehiclePose()
            blackboard.client.sim_epochs += 1
            # reset the drone back to its starting location
            pose.position = airsim.Vector3r(0, 0, 0)
            blackboard.client.simSetVehiclePose(pose, True)
            
            if blackboard.client.sim_epoch_count > blackboard.client.sim_epoch_limit:
                break
            # Reset the start time
            #start_time = time.perf_counter()
            #blackboard.drone.landed_state = False
        """

        if blackboard.sim.status == py_trees.common.Status.SUCCESS:
            break

        #times.append(round(elapsed_time))
        power = getPowerFromThrust()
        power_i.append(power)

        vel = blackboard.client.getMultirotorState().kinematics_estimated.linear_velocity.get_length()
        lv = blackboard.client.getMultirotorState().kinematics_estimated.linear_velocity.get_length()
        vel_i.append(vel)
        
        # This assumes constant velocity which is NOT the case
        # distanceZ.append((vel_z*elapsed_time))

        centroid_thrusts.append(getCentroidThrust())
        four_thrusts.append(getThrusts())

        distance_i.append((vel*elapsed_time))

        # NOTE: This BT is ticking at 500ms, therefore the rate of power computed is not once every second, its once every millisecond
        #dronePower += getPowerFromThrust(blackboard.drone.rotors.power, elapsed_time)
        #dronePower += power


        # At every BT tick, lets record the drone velocity, and instantaneous power consumed
        #print("Drone power: W " + str(dronePower))

        behavior_tree.tick()
        time.sleep(0.5)
    print("\n")

    elapsed_time = time.perf_counter() - start_time
    total_distance = np.trapz(vel_i, dx=0.5)

    # Elapsed time is measured in seconds, but BT ticks every 500ms
    et_ms = int(elapsed_time)*1000

    # Create a list of time intervals, stepping every 500ms
    # Python range is not upperbounds inclusive, so we need to increase max value by increment amount so range IS upper inclusive
    time_intervals = list(range(0, et_ms, 500))

    #distances = list(range(0, int(total_distance)))
    distances = list(range(0, int(total_distance)))

    # Since power is measured at 500ms we need to double the time taken. 
    #time_intervals = list(range(0, (int(elapsed_time)*2)-1))
    print("TIME INTERVALS:")
    print(time_intervals)

    print("VELOCITIES:")
    print(vel_i)

    print("POWERI\n")
    print(power_i)

    print("Centroid Thrusts:")
    print(centroid_thrusts)

    print("Four Thrusts:")
    print(four_thrusts)

    #power_i = power_i[:len(distances)]



    f = open("\Masters Thesis Code\Airsim py_tree controller\distance_power_data.csv", "w")
    writer = csv.writer(f)
    writer.writerows(zip(distances, power_i[:len(distances)]))
    f.close()

    dist_pwr_visual = Waypoint_visualization.Waypoint_visualization(distances, power_i[:len(distances)])
    #dist_pwr_visual = Waypoint_visualization.Waypoint_visualization(distances, power_i)
    dist_pwr_visual.visualize(
        title="Instantaneous Power (W) with Respect to Total Distance (m) Travelled",
        xlabel="Distance (m)",
        ylabel="Power (W)"
    )

    veli_pwr_visual = Waypoint_visualization.Waypoint_visualization(vel_i, power_i)
    veli_pwr_visual.visualize(
        title="Instantaneous Power (W) with Respect to Instant Velocity (m/s)",
        xlabel="Velocity (m/s)",
        ylabel="Power (W)"
    )

    cthrust_pwr_visual = Waypoint_visualization.Waypoint_visualization(time_intervals, centroid_thrusts)
    cthrust_pwr_visual.visualize(
        title="Centroid Thrust (N) with Respect to Time (ms)",
        xlabel="Time (ms)",
        ylabel="Centroid Thrust (N)"
    )

    """four_thrust_pwr_visual = Waypoint_visualization.Waypoint_visualization(four_thrusts, power_i)
    four_thrust_pwr_visual.multiDimensionalVisualize(
        title="Instantaneous Power (W) with Respect to Four Rotor Thrusts (N)",
        xlabel="Rotor Thrust (N)",
        ylabel="Power (W)",
        colors=["red", "green", "blue", "yellow"],
        labels=["rotor 1", "rotor 2", "rotor 3", "rotor 4"]
    )"""

    # Need to produce a plot of instant power over its corresponding point in time, followed by a summation of Ipower over Ttime

    f = open("\Masters Thesis Code\Airsim py_tree controller\power_time_data.csv", "w")
    writer = csv.writer(f)
    writer.writerows(zip(time_intervals, power_i))
    f.close()

    pwr_time_visual = Waypoint_visualization.Waypoint_visualization(time_intervals, power_i)
    pwr_time_visual.visualize(
        title="Instantaneous Power (W) with Respect to Time (ms)",
        xlabel="Time (ms)",
        ylabel="Power (W)"
    )

except KeyboardInterrupt:


    pass

