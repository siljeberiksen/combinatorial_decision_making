from z3 import *
import numpy as np
import heapq
import time
import json
import os


def all_variables(m, n, li, sj, D):

  # Let's define the minimum of places travelled by all couriers
  # First possiblity : all couriers take at least one item. Then it will remain n-m items.
  # So the max ammount of places travelled by a courier will be n-m (taking all the remaining items) + 1 (taking his/her first item like other couriers) + 1 (the depot)
  # Second possibility : the couriers do not have enough space to take all the remaining items (n-m). Then it will have max_item_per_courier + 1 (the depot)

  sj_sorted = sorted(sj)
  max_li = max(li)
  max_item_per_courier_option_2 = 0
  i = 0
  while max_li >= 0 and i != (len(sj_sorted)) :
    max_li = max_li - sj_sorted[i]
    if max_li < 0:
      max_li = max_li + sj_sorted[i]
      break
    else:
      i = i + 1
      max_item_per_courier_option_2 = max_item_per_courier_option_2 + 1

  max_places_travelled_opt_2 = max_item_per_courier_option_2 + 1
  # Then we take the minimum of the two posssibilities

  max_places_travelled = min(max_places_travelled_opt_2, n - m + 2)

  D_1 = np.array(D)
  # First possibility : the sum of the maximum of each row of the distance's matrix D
  max_distance_per_courier_opt_1 = sum(np.max(row) for row in D_1)

  # Second possibility : the courier can move only max_places_travelled,
  # then we can just take the max_places_travelled + 1 first max distances of the list since we have max_places_travelled places there are max_places_travelled + 1 distances
  max_distance_per_courier_opt_2 = sum(heapq.nlargest(max_places_travelled + 1, D_1.flatten()))
  max_distance_per_courier = min(max_distance_per_courier_opt_1, max_distance_per_courier_opt_2)

  # The routes can be asymetrics, so since the depot is n + 1 in D (python list start from 0 so it is n), we look the minimum of these :
  min_distance_per_courier = min([D[n][i] + D[i][n] for i in range(n)])

  # all_incrementation_variables
  COURIERS = range(m)
  ITEMS = range(n)
  LOCATIONS = range(n+1)
  MAX_PLACES_TRAVELLED = range(max_places_travelled+1)
  MAX_ROAD_TRAVELLED = range(max_places_travelled)


  dict_all_variables = {"m" : m, "n" : n, "li" : li, "sj" : sj, "D" : D,
                   "COURIERS" : COURIERS, "ITEMS" : ITEMS, "LOCATIONS" : LOCATIONS, "MAX_PLACES_TRAVELLED" : MAX_PLACES_TRAVELLED, "MAX_ROAD_TRAVELLED" : MAX_ROAD_TRAVELLED,
                   "max_places_travelled" : max_places_travelled,
                   "max_distance_per_courier" : max_distance_per_courier, "min_distance_per_courier" : min_distance_per_courier
                   }

  return dict_all_variables


# Code from the practical session with n-queen and sudoku problem
# Will be used in the constraints part

from z3 import *
from itertools import combinations

def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name = ""):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)])

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one_np(bool_vars), at_most_one_np(bool_vars, name))


def at_least_one_seq(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints)

def exactly_one_seq(bool_vars, name):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))



# Definition of all the constraints

def add_courier_capacity_constraints(solver, courier_at_location_per_movement, couriers, courier_capacities, items, item_sizes, max_places_travelled):

    contraintes = []

    for c in couriers:
        for i in items:
            for j in range(1, max_places_travelled): # Start at one because the courier is at the depot at the origin so there is no item.
                contraintes.append((courier_at_location_per_movement[c][i][j], item_sizes[i]))
        # PbLe ensure that the weight of the item pick up is lower or equal to the load of the courier c.
        solver.append(PbLe(contraintes, courier_capacities[c]))
        contraintes = []


def ensure_each_item_delivered_exactly_once(solver, courier_at_location_per_movement, couriers, items, max_places_travelled):

    for i in items:
        # Create the list of courier movements for each item
        item_movements = []
        for c in couriers:
            for j in range(1, max_places_travelled):
                item_movements.append(courier_at_location_per_movement[c][i][j])

        # Exactly once enable us to have one item i per courier
        solver.add(exactly_one_seq(item_movements, f"Item_{i}"))

def ensure_each_couriers_deliver_at_least_one_item(solver, courier_at_location_per_movement, couriers, items):

    for c in couriers:
        # Prepare the list of first movements for each courier
        first_movements = []
        for i in items:
            first_movements.append(courier_at_location_per_movement[c][i][1])

        # check the first movement of the courier where he should have get his item otherwise the movement is useless.
        solver.add(Or(first_movements))

def ensure_couriers_at_one_place(solver, courier_at_location_per_movement, couriers, places_travelled, locations):

    for c in couriers:
        for p in places_travelled:
            # Prepare the list of courier movements for each location
            courier_movements = []
            for l in locations:
                courier_movements.append(courier_at_location_per_movement[c][l][p])

            # Check for a courier c the list of courier_at_location_per_movement with all different movement and location.
            solver.add(exactly_one_seq(courier_movements, f"Courier_{c}_Movement{p}"))

def ensure_couriers_return_to_start(solver, courier_at_location_per_movement, couriers, n, max_places_travelled):

    for c in couriers:
        # First place is 0 and the last one is max_places_travelled, since the courier can not do more than max_places_travelled movement.
        start_and_end = [
            courier_at_location_per_movement[c][n][0],
            courier_at_location_per_movement[c][n][max_places_travelled]
        ]

        solver.add(*start_and_end)

def add_movement_constraints(solver, courier, location, courier_at_location_per_movement, routes,  max_roads):

    for c in courier:
        for r in max_roads:
            for i in location:
                for j in location:
                    # Add constraint: if courier is at location i at time r and at location j at time r+1, then the route between i and j is taken
                    solver.add(Implies(And(courier_at_location_per_movement[c][i][r],
                                           courier_at_location_per_movement[c][j][r + 1]),
                                       routes[c][i][j]))




def add_distance_constraint(solver, couriers, locations, courier_at_location_per_movement, routes, n, D, max_places_travelled, upper_bound):

    for c in couriers:
        distances = [(routes[c][i][j], D[i][j]) for i in locations for j in locations]
        solver.append(PbLe(distances, upper_bound))

    # Convert list of lists to numpy array and flatten, then filter strictly positive distances
    D_array = np.array(D)
    distances_positive = np.sort(D_array[D_array > 0].flatten())

    number_of_possible_movement = 0

    for movement in range(n):
        if np.sum(distances_positive[:movement + 1]) > upper_bound:
            break
        number_of_possible_movement = number_of_possible_movement + 1

    if number_of_possible_movement < max_places_travelled:
        for c in couriers:
            solver.add(courier_at_location_per_movement[c][n][number_of_possible_movement + 1])


# To obtain solution and the travel of couriers.

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
        print(f"Courier {c+1}:")
        print()

        # Collect locations visited by the courier at each time step
        locations_at_movement = {}
        for p in MAX_PLACES_TRAVELLED:
            for l in LOCATIONS:
                if is_true(model.evaluate(courier_at_location_per_movement[c][l][p])):
                    locations_at_movement[p] = l

        # Use the collected locations to determine the routes taken
        sorted_routes = []
        for p in range(len(locations_at_movement) - 1):
            i = locations_at_movement[p]
            j = locations_at_movement[p + 1]
            if is_true(model.evaluate(routes[c][i][j])):
                sorted_routes.append((i, j, D[i][j]))

        # Print sorted routes
        for route in sorted_routes:
            print(f"Route from {route[0]} to {route[1]} by courier {c} is taken with distance {route[2]}")

        # Collect locations visited excluding the depot
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


# The MCP resolution !
def MCP(m, n, li, sj, D, instance_name, time_limit = 300):


    # 1) Import all the variables needed

    working_variables = all_variables(m, n, li, sj, D)

    max_places_travelled = working_variables["max_places_travelled"]
    COURIERS = working_variables["COURIERS"]
    LOCATIONS = working_variables["LOCATIONS"]
    ITEMS = working_variables["ITEMS"]
    MAX_PLACES_TRAVELLED = working_variables["MAX_PLACES_TRAVELLED"]
    MAX_ROAD_TRAVELLED = working_variables["MAX_ROAD_TRAVELLED"]

    original_upper_bound = working_variables["max_distance_per_courier"]
    lower_bound = working_variables["min_distance_per_courier"]
    upper_bound = original_upper_bound

    pivot = (original_upper_bound + lower_bound) // 2


    solver = Solver()
    solver.set("timeout", 300000)
    start_time = time.time()


    # 2) Definiton of global variables.

    # Saying that a courier travel for j to i. ie routes[0][1][2] == true, the courier 1 is traveling trough location 2 to location 3.
    routes = [[[Bool(f"route_{c}_{j}_{i}") for i in LOCATIONS] for j in LOCATIONS] for c in COURIERS]

    # Saying at at which location is a courier depending on his number of location changes. ie :  courier_at_location_per_movement[0][1][1] == true, the courier 1 is a location 2 on is second change of location.
    courier_at_location_per_movement = [[[Bool(f"courier_at_location_per_movement_{c}_{l}_{p}") for p in MAX_PLACES_TRAVELLED] for l in LOCATIONS] for c in COURIERS]

    # 3) Definition of the constaints

    # Assure the coherence between the two global variables. If a courier c go from the place i to place j (routes[c][i][j]),
    # the courier_at_location_per_movement variable must had a movement to the courier and indicate at which place he is (And(courier_at_location_per_movement[c][i][p],
    # courier_at_location_per_movement[c][j][p+1])).
    add_movement_constraints(solver, COURIERS, LOCATIONS, courier_at_location_per_movement, routes, MAX_ROAD_TRAVELLED)

    # All the rest of the constraints.

    # Courrier capacity constraint which limits the couriers'loads to their max_capacities
    add_courier_capacity_constraints(solver, courier_at_location_per_movement, COURIERS, li, ITEMS, sj, max_places_travelled)
    # Ensure that each item is delivered once and pick up once
    ensure_each_item_delivered_exactly_once(solver, courier_at_location_per_movement, COURIERS, ITEMS, max_places_travelled)
    # Ensure that each item is delivered once and pick up once
    ensure_each_couriers_deliver_at_least_one_item(solver, courier_at_location_per_movement, COURIERS, ITEMS)
    # Ensure that a courier is at one place at a time
    ensure_couriers_at_one_place(solver, courier_at_location_per_movement, COURIERS, MAX_PLACES_TRAVELLED, LOCATIONS)
    # Ensure that each couriers return the depot
    ensure_couriers_return_to_start(solver, courier_at_location_per_movement, COURIERS, n, max_places_travelled)


    # 4) Minimising part.

    solution = None
    best_pivot = None
    # Count the number of trials needed to get the final solution.
    trial = 1

    while True:

      current_time = time.time()
      if lower_bound >= upper_bound or round(current_time - start_time, 3) >= 300:

        # Save as json file the results

        print(f"Best Trial : {best_trial}.")
        execution_time = round(current_time - start_time, 3)

        if execution_time < 300:
          optimal = True
        else:
          optimal = False

        save_results(solution, best_pivot, execution_time, optimal, instance_name)

        return solution, best_pivot, execution_time

      print()
      print(f"pivot : {pivot}")
      print()
      solver.push()

      # Adding the minimizing function.
      add_distance_constraint(solver, COURIERS, LOCATIONS, courier_at_location_per_movement, routes, n, D, max_places_travelled, pivot)
      remaining_time = time_limit - (current_time - start_time)
      solver.set("timeout", int(remaining_time * 1000))
      # If the solver find a solution for the pivot.
      result = solver.check()


      check_start_time = time.time()
      result = solver.check()
      check_end_time = time.time()
      elapsed_time = check_end_time - start_time

      print(f"Time for solver.check(): {check_end_time - check_start_time} seconds")
      print(f"Total elapsed time: {elapsed_time} seconds")

      if elapsed_time >= time_limit:
          print("Timeout reached during solver.check()")
          break

      if result == sat:

        res = solver.model()
        end_time = time.time()  # end time
        execution_time = round(end_time - start_time, 3)
        print(f"Trial : {trial}. Statut : Passed.")
        print(f"Time passed : {execution_time}.")

        # Results for the trial.
        # Couriers routes and distances travelled + the items carried by each of them.
        solution = items_per_couriers(m, n, li, sj, D, courier_at_location_per_movement, routes, solver)
        # Max distance travelled for a courier.
        best_pivot = pivot
        best_trial = trial
        print(solution)
        # Iterative operations
        trial = trial + 1
        upper_bound = pivot
        pivot = (upper_bound + lower_bound) // 2

      # The solution is unsat, we need to check if it is just this possibility or the instance.
      else:

        print(f"Trial : {trial}. Statut : Failed")
        if upper_bound == original_upper_bound:

          end_time = time.time()  # end time
          execution_time = round(end_time - start_time, 3)
          save_results(None, None, execution_time, False)

          return "Model is unsat", execution_time

        # Iterative operations
        trial = trial + 1
        lower_bound = pivot + 1
        solver.pop()
        pivot = (upper_bound + lower_bound) // 2

    end_time = time.time()
    execution_time = round(end_time - start_time, 3)
    save_results(None, None, execution_time, False, instance_name)
    return solution, best_pivot




# To read an instance and extract m, n, li, sj, D.

def read_instance_data(file_path):
    """ Lire les données d'instance d'un fichier et les convertir en paramètres utilisables pour le modèle.

    :param file_path: Chemin vers le fichier contenant les données de l'instance.
    :return: Tuple contenant m, n, li, sj, D.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        li = list(map(int, lines[2].strip().split()))
        sj = list(map(int, lines[3].strip().split()))
        D = [list(map(int, line.strip().split())) for line in lines[4:]]
    return m, n, li, sj, D


# To use an MCP function. 
def process_instance(file_path, time_limit=300):

    # Extract instance name from file path
    instance_name = file_path.split('/')[-1].split('.')[0]
    
    # Read instance data from file
    m, n, li, sj, D = read_instance_data(file_path)
    
    # Call MCP with extracted parameters
    return MCP(m, n, li, sj, D, instance_name, time_limit)

file_path = 'Instances/inst10.dat'
result = process_instance(file_path)