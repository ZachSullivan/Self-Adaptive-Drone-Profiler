import py_trees
import time

class FlyInDirection(py_trees.behaviour.Behaviour):

    def __init__(self, direction, velocity=2):
        super().__init__()
        self.api_start_time = time.perf_counter()
        self.duration = 20
        self.velocity = velocity
        self.direction = waypoints
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