import py_trees
import airsim

class Terminate(py_trees.behaviour.Behaviour):

    def __init__(self, name="Terminate"):
        super(Terminate, self).__init__(name)
        
        # Provide access to the BT blackboard
        self.blackboard = self.attach_blackboard_client("Airsim")

        self.blackboard.register_key(
            key="sim/status", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="sim/status", 
            access=py_trees.common.Access.READ
        )
        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.READ
        )

    def update(self):

        # Teleport the drone back to the start, check if successful
        pose = self.blackboard.client.simGetVehiclePose()
        pose.position.x_val = 0
        pose.position.y_val = 0
        pose.position.z_val = 0
        self.blackboard.client.simSetVehiclePose(pose, True)
        status  = py_trees.behaviour.common.Status.SUCCESS
        self.blackboard.sim.status = status
        return status


