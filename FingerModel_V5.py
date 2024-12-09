'''
Reframed 2d, TODO Into 3D
Model of 2d frame

"Curved Fingertip"
Add torque on the grasping object
'''
import numpy as np

class Finger:
    def __init__(self, pulley_list, linkage_list, contact_list, angle_list, routing, tendon_number, tendon_forces):
        self.pulley_list = pulley_list  #
        self.linkage_list = linkage_list           
        self.routing = routing  # input as a matrix with input as 1 or -1
        self.contact_list = contact_list  # The first contact TODO smarter way
        self.angle_list = angle_list
        self.tendon_number = tendon_number  # number of tendon, double examined in column# of routing matrix
        self.tendon_forces = tendon_forces  # Now accepts a list

    def set_fingertip_normal(self):

        reference = self.contact_list[-1]
        vector_start = np.array([0, 1])
        vector_end = np.array([2, 1]) / np.sqrt(5)

        normalized_value = (reference - 0.1) / (0.9 - 0.1)
        adjusted_value = normalized_value ** 2

        result_vector = vector_start + adjusted_value * (vector_end - vector_start)

        return result_vector

    def set_tendon_forces(self, forces):
        """
        Updates the tendon forces attribute.

        Parameters:
            forces (list): A list of forces to be applied to the tendons.
        """
        if len(forces) != self.tendon_number:
            raise ValueError(f"Expected {self.tendon_number} forces, but got {len(forces)}.")
        self.tendon_forces = forces

    def pulley2mat(self):
        """
        Converts a list of radii into a diagonal matrix.

        Parameters:
            radii (list or array): List of radii [r1, r2, ..., rn].

        Returns:
            numpy.ndarray: A diagonal matrix with the radii as the diagonal elements.
        """
        return np.diag(self.pulley_list)
    
    def tendon_jacob(self):
        # Use the routing matrix directly
        # Return matrix where number indicate routed pulley radius, sign indicate directions
        # Column number indicate tendon number, Row number indicate pulley number
        return np.matmul(self.pulley2mat(),self.routing)
    
    def tendonforce2mat(self, forces):
        # Row force -> Column force
        if len(forces) != self.tendon_number:
            raise ValueError(f"Expected {self.tendon_number} forces, but got {len(forces)}.")
        
        return np.array(forces).reshape(-1, 1)

    def calculate_torque(self):
        jacobian = self.tendon_jacob()
        force_vector = self.tendonforce2mat(self.tendon_forces)
        return np.matmul(jacobian, force_vector)

    def generate_force_pos(self):
        result = []

        for i in range(len(self.contact_list)):
            result.append(self.contact_list[i]*self.linkage_list[i])

        return result

    def generate_frame(self):

        frame_list = []

        cumulative_theta = 0  # To accumulate theta values
        for t in self.angle_list:
            cumulative_theta += t  # Add the current theta to the cumulative sum
            # Compute the rotation matrix for the current cumulative theta
            rotation_matrix = np.array([
                [np.cos(cumulative_theta), -np.sin(cumulative_theta)],
                [np.sin(cumulative_theta), np.cos(cumulative_theta)]
            ])
            frame_list.append(rotation_matrix)  # Append the rotation matrix to the list

        return frame_list

    def contact_jacob(self):
        """
        Compute the contact Jacobian matrix for arbitrary location_force and theta_list.

        Parameters:
            location_force (list): A list of location force components.
            theta_list (list): A list of angles (theta values).

        Returns:
            np.ndarray: The resulting contact Jacobian matrix.
        """
        n = len(self.contact_list)
        force_pos = self.generate_force_pos()

        # Initialize an n x n Jacobian matrix with zeros
        jacobian = np.zeros((n, n))

        # Populate the diagonal entries
        for i in range(n):
            jacobian[i, i] = force_pos[i]

        for i in range(n):
            for j in range(i,n):
                jacobian[i, j] = force_pos[j]
        
        # i is column number, j is row number
        shrinked_angle_list = self.angle_list[1:]
        for i in range(1, n):
            cumulative_theta = 0
            cumulative_arm = 0
            for j in range(i-1, -1, -1):
                cumulative_theta += shrinked_angle_list[j]
                cumulative_arm += self.linkage_list[j] * np.cos(cumulative_theta)
                jacobian[j, i] += cumulative_arm

        return jacobian

    def get_contact_force(self):
        # Friction cone

        mu = 0.5 # Coefficient of friction
        jacobian = self.contact_jacob()
        
        jacobian_pinv = np.linalg.pinv(jacobian)
        
        force_value = jacobian_pinv @ self.calculate_torque()
        frame_list = self.generate_frame()

        force_vector_list = [np.array([[(-1)**i*mu],[1]]) for i in range(6)] #friction cone

        end_force_vector = self.set_fingertip_normal()
        normal_end_force_vector = np.array([-end_force_vector[1], end_force_vector[0]])
        force_vector_list[-1] = end_force_vector + normal_end_force_vector * mu
        force_vector_list[-2] = end_force_vector - normal_end_force_vector * mu
        
        result_force_list = []
        for i in range(3):
            
            y1 = np.matmul(frame_list[i],force_vector_list[2*i])
            y2 = np.matmul(frame_list[i],force_vector_list[2*i+1])
            result_force_list.append((force_value[i]*y1).flatten().astype(float))
            result_force_list.append((force_value[i]*y2).flatten().astype(float))

        return result_force_list

    def get_contact_mirrored_force(self):

        mirrored_list = [np.array([-x, y]) for x, y in self.get_contact_force()]
        return mirrored_list
    
    def get_object_torque(self):
        item = self.generate_frame()
        return item

if __name__ == "__main__":
    # test
    pulley_list = [10, 10, 10]
    linkage_list = [100, 100, 100]
    routing = np.array([[1.0, 1.0, 1.0, 1.0], [0.0, 1.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0]])
    contact_list = [0.9, 0.1, 0.9]
    angle_list = [0.7853981633974483, 0.3, 0.6435011087932844]
    tendon_number = 4
    tendon_forces = [50, 50, 50, 50]

    test = Finger(pulley_list, linkage_list, contact_list, angle_list, routing, tendon_number, tendon_forces)
    
    contact_force = test.get_contact_force() + test.get_contact_mirrored_force()
    contact_force = [i.tolist() for i in contact_force]
    print(test.generate_frame())