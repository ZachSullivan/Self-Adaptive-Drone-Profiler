import py_trees
import airsim

class TakeoffAction(py_trees.behaviour.Behaviour):

    def __init__(self, name="Takeoff", velocity=0, targetAltitude=2):
        super(TakeoffAction, self).__init__(name)
        
        # Provide access to the BT blackboard
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
            key="drone/landed_state", 
            access=py_trees.common.Access.WRITE
        )
        self.blackboard.register_key(
            key="drone/landed_state", 
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

        self.name = name
        self.isComplete = False
        self.target_altitude = targetAltitude
        self.velocity = velocity
        
        self.canTakeoff = True

    def initialise(self):

        self.blackboard.client.confirmConnection()
        self.blackboard.client.enableApiControl(True)

        self.blackboard.drone.landed_state = False
        if self.isComplete == False or self.canTakeoff == False:

            print(self.name + " initalising..")
            self.canTakeoff = True
        
    def update(self):
        """
        new_status = py_trees.common.Status.RUNNING

        if self.canTakeoff == True:
            print("TAKING OFF!!!")
            self.blackboard.client.takeoffAsync()    
            self.canTakeoff = False
        else:
            self.blackboard.drone.height = self.blackboard.client.getDistanceSensorData(distance_sensor_name="Height").distance
        
            print ("ALTITUDE: " + str(round(self.blackboard.drone.height)))

            if round(self.blackboard.drone.height) == self.target_altitude:
                new_status = py_trees.common.Status.SUCCESS

        return new_status """
        self.blackboard.drone.height = self.blackboard.client.getDistanceSensorData(distance_sensor_name="Height").distance

        print("Altitude: " + str(round(self.blackboard.drone.height)))

        if round(self.blackboard.drone.height) >= self.target_altitude:
                    
            new_status = py_trees.common.Status.SUCCESS
            self.isComplete = True

        # Check if the behavior has completed
        if self.isComplete == True:
            print(self.name + " Successfull")
            new_status = py_trees.common.Status.SUCCESS
        
        # Behavior has either not yet started or is currently running
        else:
            print("TAKING OFF")
            print("TAKE OFF VELOCITY IS: " + str(self.velocity))
            new_status = py_trees.common.Status.RUNNING
            # Provide the drone with an upwards velocity impulse, along z axis, for 1 seconds
            self.blackboard.client.moveByVelocityAsync(0, 0, self.velocity, 0.5)     
            #self.blackboard.client.takeoffAsync()
        return new_status


