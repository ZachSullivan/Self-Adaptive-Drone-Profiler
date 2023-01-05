import py_trees
import time

class FlyOnPath(py_trees.behaviour.Behaviour):

    def __init__(self, waypoints, velocity=2):
        super().__init__()
        self.api_start_time = time.perf_counter()

        self.velocity = velocity
        self.waypoints = waypoints

        self.blackboard = self.attach_blackboard_client("Airsim")

        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="client", 
            access=py_trees.common.Access.READ
        )
        
    def update(self):
