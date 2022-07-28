import py_trees


class GetBBTarget(py_trees.behaviour.Behaviour):
    """Given a suite of waypoints, checks if there are any targets yet to be reached"""

    def __init__(self, waypoints):
        super().__init__()

        self.waypoints = waypoints
        self.index=0
        self.blackboard = self.attach_blackboard_client("Airsim")
        self.finished = False

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

    def _get_target(self):
        target = None
        if self.waypoints == None:
            target = None
        else:
            if self.index < len(self.waypoints):
                target = self.waypoints[self.index]
                self.index += 1

        return target
    
    def initialise(self):
    
        if self.blackboard.drone.target == None:
            return py_trees.common.Status.RUNNING

    def update(self):

        print("TESTING")



        # Get Target will keep setting the blackboard target until Get target runs out of targets to retrieve from the blackboard's waypoint list

        # If the blackboard target is empty it can either be due to the flyToTarget behavior has finished, or there are no more targets
        # Attempt to get more targets, will return none if no targets
        if self.blackboard.drone.target == None:
            self.blackboard.drone.target = self._get_target()
            if self.blackboard.drone.target == None:
                status = py_trees.common.Status.FAILURE
            else:
                print("GET TARGET: found a target!")
                print(self.blackboard.drone.target)
                status = py_trees.common.Status.SUCCESS
        else:
            status = py_trees.common.Status.RUNNING

        return status
