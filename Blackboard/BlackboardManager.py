import py_trees
class BlackboardManager(object):
    """description of class"""

    def __init__(self, name="Default"):
        self.blackboard = py_trees.blackboard.Client(name=name)
        
    def registerKey(self, key="Default_Key"):    
        self.blackboard.register_key(key=key, access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key=key, access=py_trees.common.Access.READ)

    def getBlackboard(self):
        return self.blackboard
        """blackboard.client = airsim.MultirotorClient()
        blackboard.client.confirmConnection()
        blackboard.client.enableApiControl(True)
        blackboard.client.armDisarm(True)
        blackboard.drone.API_timeout = 10000   # Timeout any movement API calls after 10 seconds
        blackboard.drone.landed_state = True"""

