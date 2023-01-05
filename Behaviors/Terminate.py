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

        self.isComplete = False

    def update(self):


        # Teleport the drone back to the start, check if successful
        pose = self.blackboard.client.simGetVehiclePose()
        print(pose.position)

        if self.isComplete == True:
            print("TERMINATION SUCCESSFUL")       
            status = py_trees.common.Status.SUCCESS
            
            self.blackboard.sim.status = status
        else:

            self.blackboard.client.hoverAsync().join()

            pose.position.x_val = 0
            pose.position.y_val = 0
            pose.position.z_val = 0
            
            self.blackboard.client.simSetVehiclePose(pose, True)
            
            self.blackboard.client.armDisarm(False)
            self.isComplete = True
            status = py_trees.common.Status.RUNNING
      
        return status


