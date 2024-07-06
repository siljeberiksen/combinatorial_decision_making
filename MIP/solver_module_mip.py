import os
import json
import time
import multiprocessing
from variables_mip import all_variables
from constraints_mip import *

# To get the item list of the couriers
def items_per_courier(m, n, li, sj, D, routes):
    # Retrieve working variables such as couriers and locations
    working_variables = all_variables(m, n, li, sj, D)
    COURIERS = working_variables["COURIERS"]
    LOCATIONS = working_variables["LOCATIONS"]

    # Initialize a list to store items for each courier
    item_per_courier_list = []

    # Iterate over each courier to determine the items they carry
    for c in COURIERS:
        # Initialize a list to store items for the current courier
        item_per_courier = []
        # Start at the depot (location n)
        current_location = n
        # Flag to indicate when the courier returns to the depot
        FINISH = False

        # Continue until the courier returns to the depot
        while not FINISH:
            # Iterate over all possible locations
            for l in LOCATIONS:
                # Check if the courier travels from the current location to location l
                if routes[c][current_location][l].varValue == 1:
                    # Update the current location to the new location
                    current_location = l
                    # If the courier returns to the depot, set FINISH to True
                    if current_location == n:
                        FINISH = True
                    else:
                        # Otherwise, add the location (item) to the list for the current courier
                        item_per_courier.append(current_location + 1)
                    # Break the loop to check the next location from the new current location
                    break

        # Append the list of items for the current courier to the overall list
        item_per_courier_list.append(item_per_courier)

    # Return the list of items per courier
    return item_per_courier_list


# To save a json file.
def save_results(solution, max_distance, execution_time, optimal, instance_name):
    # Extract numeric part from instance name, e.g., "inst01.dat" -> "1"
    instance_number = int(''.join(filter(str.isdigit, instance_name)))
    # Generate the filename based on the instance number
    filename = f'{instance_number}.json'
    
    # Define the path to save the file
    save_path = os.path.join('res', 'MIP')
    
    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(save_path, filename)

    results = {
        "PULP_CBC_CMD": {
            "time": float(execution_time),
            "optimal": optimal,
            "obj": int(max_distance) if max_distance is not None else None,
            "sol": solution
        }
    }

    # Save results to the file in the specified path
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=4)


def objective_distance(m, n, li, sj, D, solution):
    # Extract working variables including couriers based on other input variables
    working_variables = all_variables(m, n, li, sj, D)
    COURIERS = working_variables["COURIERS"]
    # Path of all couriers
    path = []
    # For each them we add the depot at the end and the beginning of his list of items picked up.
    for c in COURIERS:
        path.append([n+1] + solution[c] + [n+1])

     # List to store the total distance each courier travels.
    distance_per_courier_list = []
     # Calculate the distance for the current path by summing up distances between consecutive points.
    for c in COURIERS:

        distance_per_courier = 0

        for l in range(1,len(path[c])):

            curr_item = path[c][l] - 1
            prev_item = path[c][l-1] - 1
            distance_per_courier = distance_per_courier + D[prev_item][curr_item]

        distance_per_courier_list.append(distance_per_courier) # Add total distance for this courier

    # Return the maximum distance traveled by any courier
    return max(distance_per_courier_list)


def MCP_MIP_PULP(m, n, li, sj, D, instance_name, solver_name = 'PULP_CBC_CMD', timeout = 300):

    # Solver definition
    # Initialize the optimization problem with the objective to minimize the maximum distance traveled by any courier
    start_time = time.time()
    model = LpProblem("MIP_Problem", LpMinimize)


    # 1) Import all the variables needed


    working_variables = all_variables(m, n, li, sj, D)
    
    COURIERS = working_variables["COURIERS"]
    LOCATIONS = working_variables["LOCATIONS"]
    ITEMS = working_variables["ITEMS"]
    max_places_travelled = working_variables["max_places_travelled"]
    upper_bound = working_variables["max_distance_per_courier"]
    lower_bound = working_variables["min_distance_per_courier"]


    # 2) Definiton of decision variables.


    # Create a 3D list of binary decision variables to represent whether a courier travels from one location to another
    # routes[c][i][j] is 1 if courier c travels from location i to location j, otherwise 0
    routes = [[[LpVariable(f"routes_{c}_{i}_{j}", cat=LpBinary) for j in LOCATIONS] for i in LOCATIONS] for c in COURIERS]
    
    # Create a 2D list of binary decision variables to represent whether a courier carries a specific package
    # item_per_courier[c][i] is 1 if courier c carries package i, otherwise 0
    item_per_courier = [[LpVariable(f"item_per_courier_{c}_{i}", cat=LpBinary) for i in ITEMS] for c in COURIERS]

    # Create a 2D list of integer decision variables to represent the path sequence of each courier
    # places_travelled_per_courier[c][l] is the sequence number of location l in the path of courier c
    places_travelled_per_courier = [[LpVariable(f"places_travelled_per_courier_{c}_{l}", lowBound=0, upBound=max_places_travelled, cat=LpInteger) for l in LOCATIONS] for c in COURIERS]

    # Create a list of integer decision variables to represent the total distance traveled by each courier
    # distance_per_courier[c] is the total distance traveled by courier c
    distance_per_courier = [LpVariable(f"distance_per_courier_{c}", lowBound=lower_bound, upBound=upper_bound, cat=LpInteger) for c in COURIERS]

    # Create an integer decision variable to represent the maximum distance traveled by any courier, which is the objective to minimize
    max_distance_per_courier = LpVariable("max_distance_per_courier", lowBound= max([D[n][i] + D[i][n] for i in ITEMS]), upBound=upper_bound, cat=LpInteger) # lowBound is the minimum of max_distance_per_courier,
                                                                                                                                                             # so it is only one item and the farthest one of the depot.

    # 3) Constraints Part


    add_depot_start_constraints(model, places_travelled_per_courier, COURIERS, n)
    add_capacity_constraints(model, item_per_courier, sj, li, COURIERS, ITEMS)
    ensure_each_item_delivered_exactly_once_constraints(model, item_per_courier, COURIERS, ITEMS)
    ensure_each_couriers_deliver_at_least_one_item_constraints(model, routes, COURIERS, ITEMS, n)
    add_path_constraints(model, routes, places_travelled_per_courier, LOCATIONS, ITEMS, COURIERS, n)
    ensure_couriers_return_to_start_constraints(model, routes, COURIERS, LOCATIONS, n)
    add_item_transport_constraints(model, routes, item_per_courier, COURIERS, ITEMS, LOCATIONS)
    add_arrival_departure_constraints(model, routes, COURIERS, ITEMS, LOCATIONS)
    add_self_loop_constraints(model, routes, COURIERS, ITEMS)
    add_distance_constraints(model, routes, D, distance_per_courier, COURIERS, LOCATIONS)
    add_max_distance_constraints(model, distance_per_courier, max_distance_per_courier, COURIERS)


    # 4) Solving Part


    # Solver choice.
    if solver_name == 'PULP_CBC_CMD':
        model.solve(PULP_CBC_CMD(msg=0, timeLimit=timeout)) # to get more info msg = 1
    else:
        raise ValueError(f"Solver {solver_name} is not supported.")
    
    # Time metric.
    end_time = time.time()
    execution_time = end_time - start_time

    # Checking the model result.
    if model.status in [1, 2]:  # 1: Optimal, 2: Feasible
        # Looking for the items of each courier.
        solution = items_per_courier(m, n, li, sj, D, routes)
        status = True
        # Calcul of the objective_distance.
        obj = objective_distance(m, n, li, sj, D, solution)
        print(f'Solution: {solution}')
        print(f'Optimal: {status}')
        print(f'obj: {obj}')
        print(f'time: {execution_time}')
        save_results(solution, obj, execution_time, status, instance_name)
        return solution, status, obj, execution_time

    # Model didn't find a solution.
    elif model.status == 0:  # 0: Not Solved
        print("Solver did not solve the model.")
        print()
    elif model.status == -1:  # -1: Infeasible
        print("Model is infeasible.")
        print()
    elif model.status == -2:  # -2: Unbounded
        print("Model is unbounded.")
        print()
    elif model.status == -3:  # -3: Undefined
        print("Model has an undefined status.")
        print()
    else:
        print(f"Unexpected status code: {model.status}")
        print()

    print(f'Solution: {None}')
    print(f'Optimal: {False}')
    print(f'obj: {None}')   
    print(f'time: {execution_time}')
    save_results(None, None, execution_time, False, instance_name)
    return None, False, None, execution_time # Return None and False if the model did not solve correctly

def wrapper(func, args, return_dict):
    result = func(*args)
    return_dict['result'] = result

def run_with_timeout(func, args, timeout, instance_name):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=wrapper, args=(func, args, return_dict))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        print("Timeout: Function exceeded time limit")
        save_results(None, None, timeout, False, instance_name)
        return None, False, None, timeout

    return return_dict.get('result', (None, False, None, timeout))