import py_trees

class LandAction(py_trees.behaviour.Behaviour):
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
        
        self.blackboard.register_key(
            key="drone/landed_state", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="drone/landed_state", 
            access=py_trees.common.Access.READ
        )

        self.isComplete = False
        self.velocity = velocity

    def initialise(self):
        print("landing initalising..")
        if self.blackboard.drone.landed_state == True:
            print("Already Landed!")
            return py_trees.common.Status.FAILURE


    def update(self):
        self.blackboard.drone.height = self.blackboard.client.getDistanceSensorData(distance_sensor_name="Height").distance

        print(round(self.blackboard.drone.height))

        # Check if the behavior has completed
        if round(self.blackboard.drone.height) == 0:
            print("Landing Successful!")
            self.blackboard.drone.landed_state = True  
            return py_trees.common.Status.SUCCESS

        # Behavior has either not yet started or is currently running
        else:
            print("Landing...")
            new_status = py_trees.common.Status.RUNNING
            # Provide the drone with an upwards velocity impulse, along z axis, for 1 seconds
            #self.blackboard.client.moveByVelocityAsync(0, 0, self.velocity, 1)     
            self.blackboard.client.landAsync()
            # TODO: either use the correct landing api call, or instruct the drone to disarm once landing has completed or deaccelerate as drone approaches landing
            # TODO: Once the drone has landed, reset the position of the drone back to the starting location, reset the simulation starttime and allow the BT to repeat for X cyles.
            # .. this would be done so that a montecarlo simulation can be conducted with a larger sample space for power over distance. Then plot a best fit regression over the scatter data

        return new_status