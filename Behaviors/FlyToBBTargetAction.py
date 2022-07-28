from sre_constants import SUCCESS
import py_trees
import time

class FlyToBBTargetAction(py_trees.behaviour.Behaviour):
    def __init__(self, duration=None):
        super().__init__()
        self.api_start_time = time.perf_counter()
        self.duration = duration
        self.target = None
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
    
    def update(self):
        target = self.blackboard.drone.target
        print("FlyToBBTarget")
        print(self.target)

        status = py_trees.common.Status.RUNNING

        # Obtain the drone's current position
        drone_pos = self.blackboard.client.simGetVehiclePose().position

        # If a timeout was give, check if behavior has timed out
        if self.duration is not None:
            elapsed_time = (time.perf_counter() - self.api_start_time)
            if elapsed_time >= self.duration:
                print("fly forward timelimit reached")
                self.isComplete = True
                return py_trees.common.Status.FAILURE          
        
        # If the blackboard does not have a target, fail the behavior
        if target != None:
            
            print(abs(round(target.x_val - drone_pos.x_val)))

            # Check if the drone is within acceptable target distance
            if abs(round(target.x_val - drone_pos.x_val)) <= 1 and abs(round(target.y_val - drone_pos.y_val)) <= 1:
                print("Destination arrived")
                # Arrived at the destination, clear the blackboard target
                self.blackboard.drone.target = None
                status = py_trees.common.Status.FAILURE
            else:
                print("Executing fly towards target behavior...")
                self.blackboard.client.moveToPositionAsync(target.x_val, target.y_val, target.z_val, 2)  
        else:
            print("Target not found, FAILED fly")
            status = py_trees.common.Status.INVALID
        

        return status