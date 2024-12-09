import numpy as np
from itertools import product
from scipy.spatial import ConvexHull
from FingerModel_V5 import Finger
import csv

# functions for computing minimum ball contained in the convex hull
def get_2D_distance(point1, point2):
    """
    Compute the distance from the origin to the infinite line passing through point1 and point2.
    """
    # Define the origin
    origin = np.array([0, 0])

    numerator = abs((point2[1] - point1[1]) * origin[0] - 
                    (point2[0] - point1[0]) * origin[1] + 
                    point2[0] * point1[1] - point2[1] * point1[0])

    denominator = np.sqrt((point2[1] - point1[1])**2 + (point2[0] - point1[0])**2)

    distance = numerator / denominator

    return distance

def get_minimum_radius(points):
    """
    Compute the radius of the smallest ball centered at the origin
    and contained in the convex hull defined by the points.
    """
    current_distance = float('inf')  # Initialize with infinity

    for i in range(len(points)):
        # Calculate distance to each edge of the convex hull
        distance = get_2D_distance(points[i - 1], points[i])  # Wraps around for the first edge
        current_distance = min(distance, current_distance)

    return current_distance

# function for getting the vertices
def minkowski_sum(polygons):
    """
    Compute the Minkowski sum of multiple polygons.
    Each polygon must be an array of 2D points.
    """
    result = []
    for combination in product(*polygons):
        summed_point = np.sum(combination, axis=0)  # Sum points in the combination
        result.append(summed_point)
    return np.array(result)

# function for getting contact list and angle list based on different configurations
def get_contact_angle_list(first_contact, first_angle, linkage_list, ball_radius):
    # Calculate the contact list
    contact_list = [
        first_contact,
        (linkage_list[0] * (1 - first_contact)) / linkage_list[1],
        (linkage_list[1] - linkage_list[0] * (1 - first_contact)) / linkage_list[2],
    ]

    # Calculate the angle list based on the valid contact list
    angle_list = [
        first_angle,
        np.pi - 2 * np.arctan(ball_radius / (linkage_list[1] * contact_list[1])),
        np.pi - 2 * np.arctan(ball_radius / (linkage_list[2] * contact_list[2])),
    ]

    return contact_list, angle_list

# Now given a variety of designs for various total pulley radius and linkage length 
routing = np.array([[1.0, 1.0, 1.0, 1.0], [0.0, 1.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0]])
tendon_number = 4

ball_radius = 250

first_angle_list = np.linspace(np.pi*1/12, np.pi*5/12, num = 5)
first_contact_list = np.linspace(0.2, 0.8, num = 5)

# tendon_force_value = np.linspace(0,50,num = 4)
# tendon_force_list = list(product(tendon_force_value, repeat=4))
tendon_forces = [50,0,50,50]

pulley_sum_list = np.linspace(30, 60, num=20)
linkage_sum_list = np.linspace(210, 400, num=90)

# Prepare CSV file
csv_file = "design_results_" + str(ball_radius) + ".csv"
csv_headers = ["Pulley Sum", "Linkage Sum", "Max Radius", "Pulley List", "Linkage List", "Best Angle", "Best Contact"]

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)

    for pulley_sum, linkage_sum in product(pulley_sum_list, linkage_sum_list):
        max_radius = 0
        best_angle = None
        best_contact = None

        min_pulley_value = pulley_sum // 6
        max_pulley_value = pulley_sum - 2 * min_pulley_value
        min_linkage_value = linkage_sum // 6
        max_linkage_value = linkage_sum - 2 * min_linkage_value

        pulley_combinations = [
            [x, y, pulley_sum - x - y]
            for x, y in product(
                np.linspace(min_pulley_value, max_pulley_value, num=6), 
                repeat=2
            )
            if min_pulley_value <= pulley_sum - x - y <= max_pulley_value
        ]

        linkage_combinations = [
            [x, y, linkage_sum - x - y]
            for x, y in product(
                np.linspace(min_linkage_value, max_linkage_value, num=6), 
                repeat=2
            )
            if min_linkage_value <= linkage_sum - x - y <= max_linkage_value
        ]

        for pulley_list, linkage_list in product(pulley_combinations, linkage_combinations):
            for first_angle, first_contact in product(first_angle_list, first_contact_list):
                try:
                    contact_list, angle_list = get_contact_angle_list(first_contact, first_angle, linkage_list, ball_radius)
                    # Check if any value in contact_list is out of range
                    if any(i > 1 or i < 0 for i in contact_list):
                        continue  # Skip this iteration entirely if the condition is met

                    finger = Finger(pulley_list, linkage_list, contact_list, angle_list, routing, tendon_number, tendon_forces)
                    contact_force = finger.get_contact_force() + finger.get_contact_mirrored_force()


                    polygon_list = [np.array([[0, 0], contact_force[2 * i], contact_force[2 * i + 1]]) for i in range(len(contact_force) // 2)]
                    minkowski_points = minkowski_sum(polygon_list)
                    minkowski_points = np.unique(minkowski_points, axis=0)

                    if len(minkowski_points) < 3:
                        continue

                    hull = ConvexHull(minkowski_points)
                    radius = get_minimum_radius(minkowski_points[hull.vertices])
                    if radius > max_radius:
                        best_linkage_list = linkage_list
                        best_pulley_list = pulley_list
                        max_radius = radius
                        best_angle = angle_list
                        best_contact = contact_list


                except Exception as e:
                    print(f"Error: {e}")
                    continue

        writer.writerow([pulley_sum, linkage_sum, max_radius, best_pulley_list, best_linkage_list, best_angle, best_contact])

print(f"Results saved to {csv_file}.")