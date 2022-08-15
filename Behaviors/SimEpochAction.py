import py_trees
import airsim
# Updates the number of epochs simuated, checks if epoch limit is reached, ends simulation
class SimEpochAction(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__()

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
            key="sim/epoch_count", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="sim/epoch_count", 
            access=py_trees.common.Access.READ
        )

        self.blackboard.register_key(
            key="sim/epoch_limit", 
            access=py_trees.common.Access.READ
        )

        self.blackboard.register_key(
            key="drone/landed_state", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="drone/landed_state", 
            access=py_trees.common.Access.READ
        )

        self.blackboard.register_key(
            key="sim/status", 
            access=py_trees.common.Access.WRITE
        )

    def update(self):
        status = py_trees.behaviour.common.Status.RUNNING

        # First increment the sim epoch by 1
        self.blackboard.sim.epoch_count += 1

        print("RESETING DRONE")
        # Get the present pose of the drone
        pose = self.blackboard.client.simGetVehiclePose()
            
        # reset the drone back to its starting location
        pose.position = airsim.Vector3r(0, 0, 0)
        self.blackboard.client.simSetVehiclePose(pose, True)
          
        # check if the new epoch count surpasses the epoch limit
        if self.blackboard.sim.epoch_count > self.blackboard.sim.epoch_limit:
            status  = py_trees.behaviour.common.Status.SUCCESS
        self.blackboard.sim.status = status
        return status




