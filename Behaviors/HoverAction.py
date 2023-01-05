import py_trees
import airsim

class HoverAction(py_trees.behaviour.Behaviour):
    def __init__(self, velocity = 2):
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
            key="drone/height", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="drone/height", 
            access=py_trees.common.Access.READ
        )
       
        self.isComplete = False

    def update(self):

        kinematic_data = self.blackboard.client.simGetGroundTruthKinematics()
        print(kinematic_data.linear_velocity)

        if (round(kinematic_data.linear_velocity.x_val) == 0 and round(kinematic_data.linear_velocity.y_val) == 0 and round(kinematic_data.linear_velocity.z_val) == 0):

            print("HOVER SUCCESSFUL")       
            status = py_trees.common.Status.SUCCESS
        else:
            print("Hovering...")
            status = py_trees.common.Status.RUNNING
 
            self.blackboard.client.hoverAsync()


        return status