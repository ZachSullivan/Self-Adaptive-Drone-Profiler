from sre_constants import SUCCESS
import py_trees
import time

class FlyToBBTargetsAction(py_trees.behaviour.Behaviour):
    def __init__(self, waypoints, duration=None):
        super().__init__()
        self.api_start_time = time.perf_counter()
        self.duration = duration
        self.waypoints = waypoints
        self.index=0
        self.blackboard = self.attach_blackboard_client("Airsim")

        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.READ
        )
        
        self.blackboard.register_key(
            key="drone/target", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="drone/target", 
            access=py_trees.common.Access.READ
        )
    
    def initialise(self):
        print("Initalizing waypoint behavior...")
        self.index = 0
        self.blackboard.drone.target = None

    def _get_target(self):
        target = None
        if self.waypoints == None:
            target = None
        else:
            if self.index < len(self.waypoints):
                target = self.waypoints[self.index]
                self.index += 1

        return target

    def update(self):
        
        if self.blackboard.drone.target == None:
            print("GETTING NEW TARGET")
            self.blackboard.drone.target = self._get_target()
            if self.blackboard.drone.target == None:
                status = py_trees.common.Status.SUCCESS
            else:
                print("Found a target!")
                target = self.blackboard.drone.target

                self.blackboard.client.moveToPositionAsync(target.x_val, target.y_val, target.z_val, 2) 
                status = py_trees.common.Status.RUNNING
        else:
            status = py_trees.common.Status.RUNNING
        
            target = self.blackboard.drone.target

            print("FlyToBBTarget")
            print(target)


            # Obtain the drone's current position
            drone_pos = self.blackboard.client.simGetVehiclePose().position

            # If a timeout was give, check if behavior has timed out
            if self.duration is not None:
                elapsed_time = (time.perf_counter() - self.api_start_time)
                if elapsed_time >= self.duration:
                    print("fly forward timelimit reached")
                    self.isComplete = True
                    return py_trees.common.Status.FAILURE          
        

            print("Executing fly towards target behavior...")
            self.blackboard.client.moveToPositionAsync(target.x_val, target.y_val, target.z_val, 2)  
            # If the blackboard does not have a target, fail the behavior

            print(abs(round(target.x_val - drone_pos.x_val)))

            # Check if the drone is within acceptable target distance
            if abs(round(target.x_val - drone_pos.x_val)) <= 1 and abs(round(target.y_val - drone_pos.y_val)) <= 1:
                print("Destination arrived")
                # Arrived at the destination, clear the blackboard target
                self.blackboard.drone.target = None
                #status = py_trees.common.Status.FAILURE

        return status