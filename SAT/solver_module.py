from z3 import Solver, sat, Bool, is_true
import time
import os
import json
from multiprocessing import Process, Manager
import numpy as np
from variables import all_variables
from constraints import add_movement_constraints, add_courier_capacity_constraints, ensure_each_item_delivered_exactly_once, ensure_each_couriers_deliver_at_least_one_item, ensure_couriers_at_one_place, ensure_couriers_return_to_start, add_distance_constraint


def items_per_couriers(m, n, li, sj, D, courier_at_location_per_movement, routes, solver):

    working_variables = all_variables(m, n, li, sj, D)

    MAX_PLACES_TRAVELLED = working_variables["MAX_PLACES_TRAVELLED"]
    COURIERS = working_variables["COURIERS"]
    LOCATIONS = working_variables["LOCATIONS"]

    model = solver.model()
    L_objects_couriers = []

    for c in COURIERS:
        L_objects_courier = []

        print()
        print(f"Courier {c + 1}:")
        print()

        # Collect locations visited by the courier at each time step.
        locations_at_movement = {}
        for p in MAX_PLACES_TRAVELLED:
            for l in LOCATIONS:
                if is_true(model.evaluate(courier_at_location_per_movement[c][l][p])):
                    locations_at_movement[p] = l

        # Use the collected locations to determine the routes taken.
        sorted_routes = []
        for p in range(len(locations_at_movement) - 1):
            i = locations_at_movement[p]
            j = locations_at_movement[p + 1]
            if is_true(model.evaluate(routes[c][i][j])):
                sorted_routes.append((i, j, D[i][j]))

        # Print sorted routes.
        for route in sorted_routes:
            print(f"Route from {route[0]} to {route[1]} by courier {c} is taken with distance {route[2]}")

        # Collect locations visited excluding the depot.
        for p in MAX_PLACES_TRAVELLED:
            if p in locations_at_movement and locations_at_movement[p] != n:
                L_objects_courier.append(locations_at_movement[p] + 1)

        L_objects_couriers.append(L_objects_courier)

    return L_objects_couriers


# To save a json file.
def save_results(solution, best_pivot, execution_time, optimal, instance_name):
    # Extract numeric part from instance name, e.g., "inst01.dat" -> "1"
    instance_number = int(''.join(filter(str.isdigit, instance_name)))
    # Generate the filename based on the instance number
    filename = f'{instance_number}.json'
    
    # Define the path to save the file
    save_path = os.path.join('res', 'SAT')
    
    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(save_path, filename)

    results = {
        "pseudo_boolean_sat": {
            "time": float(execution_time),
            "optimal": optimal,
            "obj": int(best_pivot) if best_pivot is not None else None,
            "sol": solution
        }
    }

    # Save results to the file in the specified path
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=4)


# Function to process the solver in a separate process and have an overall timer.
def solver_process(result_dict, pivot, start_time, time_limit, m, n, li, sj, D):
    # Use to have an overall timer. It will stop the execution after 300s. We did this since the set from z3 was not working on certain instances.
    try:
        # Solver definition
        solver = Solver()  # Create the solver inside the process
        solver.set("timeout", int(time_limit * 1000))  # Set the timeout in milliseconds

        # 1) Import all the variables needed
        working_variables = all_variables(m, n, li, sj, D)
        max_places_travelled = working_variables["max_places_travelled"]
        COURIERS = working_variables["COURIERS"]
        LOCATIONS = working_variables["LOCATIONS"]
        ITEMS = working_variables["ITEMS"]
        MAX_PLACES_TRAVELLED = working_variables["MAX_PLACES_TRAVELLED"]
        MAX_ROAD_TRAVELLED = working_variables["MAX_ROAD_TRAVELLED"]
        
        # 2) Definiton of decision variables.

        # Saying that a courier travel for j to i. ie routes[0][1][2] == true, the courier 1 is traveling trough location 2 to location 3.
        routes = [[[Bool(f"route_{c}_{j}_{i}") for i in LOCATIONS] for j in LOCATIONS] for c in COURIERS]
        # Saying at at which location is a courier depending on his number of location changes. ie :  
        # courier_at_location_per_movement[0][1][1] == true, the courier 1 is a location 2 on is second change of location.
        courier_at_location_per_movement = [[[Bool(f"courier_at_location_per_movement_{c}_{l}_{p}") for p in MAX_PLACES_TRAVELLED] for l in LOCATIONS] for c in COURIERS]


        # 3) Definition of the constaints

        # Assure the coherence between the two decision variables. If a courier c go from the place i to place j (routes[c][i][j]),
        # the courier_at_location_per_movement variable must had a movement to the courier and indicate at which place he is (And(courier_at_location_per_movement[c][i][p],
        # courier_at_location_per_movement[c][j][p+1])).
        add_movement_constraints(solver, COURIERS, LOCATIONS, courier_at_location_per_movement, routes, MAX_ROAD_TRAVELLED)

        # All the rest of the constraints.

        # Courrier capacity constraint which limits the couriers'loads to their max_capacities.
        add_courier_capacity_constraints(solver, courier_at_location_per_movement, COURIERS, li, ITEMS, sj, max_places_travelled)
        # Ensure that each item is delivered once and pick up once.
        ensure_each_item_delivered_exactly_once(solver, courier_at_location_per_movement, COURIERS, ITEMS, max_places_travelled)
        # Ensure that each courier deliver at least one item.
        ensure_each_couriers_deliver_at_least_one_item(solver, courier_at_location_per_movement, COURIERS, ITEMS)
        # Ensure that a courier is at one place at a time
        ensure_couriers_at_one_place(solver, courier_at_location_per_movement, COURIERS, MAX_PLACES_TRAVELLED, LOCATIONS)
        # Ensure that each couriers return the depot
        ensure_couriers_return_to_start(solver, courier_at_location_per_movement, COURIERS, n, max_places_travelled)
        
        # 4) Minimising part.
        add_distance_constraint(solver, COURIERS, LOCATIONS, courier_at_location_per_movement, routes, n, D, max_places_travelled, pivot)

        result = solver.check()
        # Checking if the result is sat.
        if result == sat:
            # Retrieve the solutions.
            solution = items_per_couriers(m, n, li, sj, D, courier_at_location_per_movement, routes, solver)
            result_dict["result"] = "sat"
            result_dict["solution"] = solution
        # Otherwise output unsat
        else:
            result_dict["result"] = "unsat"
    # In case there is an error
    except Exception as e:
        result_dict["result"] = "error" # Indicate that an error occurred.
        result_dict["error"] = str(e)   # Store the error message in the shared dictionary.
    # Thanks to multiprocessing we can have on timer that checks if the time is reaching 300s
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        result_dict["execution_time"] = execution_time


# Function to solve the problem.
def MCP(m, n, li, sj, D, instance_name, time_limit=300):

    # 1) Import all the variables needed, mainly for the minimisation part.
    working_variables = all_variables(m, n, li, sj, D)

    original_upper_bound = working_variables["max_distance_per_courier"]
    lower_bound = working_variables["min_distance_per_courier"]
    upper_bound = original_upper_bound
    pivot = (original_upper_bound + lower_bound) // 2

    start_time = time.time()

    solution = None
    best_pivot = None
    # Count the number of trials needed to get the final solution.
    trial = 1

    while True:
        # Current time
        current_time = time.time()
        # In this case the problem is solve.
        if lower_bound >= upper_bound:
            print(f"Best Trial : {best_trial}.")
            # Calcul of the time
            execution_time = round(current_time - start_time, 3)
            # To be sure the result it is under the timeout.
            optimal = execution_time < time_limit
            # Save the result in the good format.
            save_results(solution, best_pivot, execution_time, optimal, instance_name)

            return solution, best_pivot, execution_time
        print()
        print(f"pivot : {pivot}")
        print()

        # Remaining time before the end of timeout.
        remaining_time = time_limit - (current_time - start_time)

        with Manager() as manager: # Create a manager to share objects between processes.

            result_dict = manager.dict() # Create a shared dictionary for storing results between processes.
            # Create a new process to run the solver_process function.
            p = Process(target=solver_process, args=(result_dict, pivot, start_time, remaining_time, m, n, li, sj, D))
            p.start()  # Start the process.
            p.join(remaining_time) # Wait for the process to finish or the remaining time to elapse.

            if p.is_alive(): # If the process is still running after the allotted time.
                p.terminate() # Terminate the process.
                p.join() # Wait for the process to fully terminate.
                result_dict["result"] = "timeout" # Set the result as "timeout" in the shared dictionary.

            exe_solver_check_time = time.time() - start_time

            if result_dict["result"] == "sat":
                # Results for the trial.
                # Couriers routes and distances travelled + the items carried by each of them.
                solution = result_dict["solution"]
                # Max distance travelled for a courier.
                best_pivot = pivot
                best_trial = trial
                end_time = time.time()
                execution_time = round(end_time - start_time, 3)
                print(f"Trial : {trial}. Status : Passed.")
                print(f"Time passed : {execution_time}.")
                print(solution)
                # Iterative operations
                trial = trial + 1
                upper_bound = pivot
                pivot = (upper_bound + lower_bound) // 2

            # The solution is unsat, we need to check if it is just this possibility or the instance.

            elif result_dict["result"] == "unsat":

                print(f"Trial : {trial}. Status : Failed")
                if upper_bound == original_upper_bound:

                    end_time = time.time()
                    execution_time = round(end_time - start_time, 3)

                    save_results(None, None, execution_time, False, instance_name)
                    
                    return "Model is unsat", execution_time

                # Iterative operations
                trial = trial + 1
                lower_bound = pivot + 1
                pivot = (upper_bound + lower_bound) // 2

            # Timeout reached.
            
            else:
                print("Timeout reached during solver.check()")
                break

            if exe_solver_check_time >= time_limit:
                print("Timeout reached during solver.check()")
                break

    # Therefor we return the best results we got.
    save_results(solution, best_pivot, 300, False, instance_name)
    return solution, best_pivot, 300