from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary, LpInteger, PULP_CBC_CMD

def add_depot_start_constraints(model, places_travelled_per_courier, COURIERS, n):
    # Adds constraints to the model ensuring that the path counter for each courier at the depot is zero.
    for c in COURIERS:
        # The path counter for each courier at the depot must be zero
        model += places_travelled_per_courier[c][n] == 0

def add_capacity_constraints(model, item_per_courier, sj, li, COURIERS, ITEMS):
    # Adds constraints to the model ensuring that the total weight of items carried by each courier does not exceed its capacity.
    for c in COURIERS:
        # The total weight of items carried by each courier must not exceed its capacity
        model += lpSum([item_per_courier[c][i] * sj[i] for i in ITEMS]) <= li[c]

def ensure_each_item_delivered_exactly_once_constraints(model, item_per_courier, COURIERS, ITEMS):
    # Adds constraints to the model ensuring that each item is assigned to exactly one courier.
    for i in ITEMS:
        # Each item must be carried by exactly one courier
        model += lpSum([item_per_courier[c][i] for c in COURIERS]) == 1

def ensure_each_couriers_deliver_at_least_one_item_constraints(model, routes, COURIERS, ITEMS, n):
    # Adds constraints to the model ensuring that each courier must transport at least one package.
    for c in COURIERS:
        # Each courier must transport at least one package
        model += lpSum([routes[c][n][l] for l in ITEMS]) == 1

def ensure_couriers_return_to_start_constraints(model, routes, COURIERS, LOCATIONS, n):
    # Adds constraints to the model ensuring that each courier enters and exits the depot exactly once.
    for c in COURIERS:
        # Each courier must exit the depot exactly once
        model += lpSum([routes[c][l][n] for l in LOCATIONS]) == 1
        # Each courier must enter the depot exactly once
        model += lpSum([routes[c][n][l] for l in LOCATIONS]) == 1

def add_path_constraints(model, routes, places_travelled_per_courier, LOCATIONS, ITEMS, COURIERS, n):
    # Adds path constraints to the model ensuring that if a courier travels from one location to another,
    # the travel path counter is incremented accordingly.
    
    # Define a sufficiently large constant used in the path constraints to enforce proper sequencing
    # big_M_constant is set to the number of items plus an additional buffer to ensure it is large enough
    big_M_constant = n + 4

    for l in LOCATIONS:
        for i in ITEMS:
            for c in COURIERS:
                # If route[c][l][i] == 1, then places_travelled_per_courier[c][i] = places_travelled_per_courier[c][l] + 1
                model += places_travelled_per_courier[c][i] - places_travelled_per_courier[c][l] <= big_M_constant * (1 - routes[c][l][i]) + 1
                model += places_travelled_per_courier[c][l] - places_travelled_per_courier[c][i] <= big_M_constant * (1 - routes[c][l][i]) - 1

def add_item_transport_constraints(model, routes, item_per_courier, COURIERS, ITEMS, LOCATIONS):
    # Adds constraints to the model ensuring that if a courier transports a package,
    # it must leave the location of the item.
    for c in COURIERS:
        for i in ITEMS:
            # If a courier carries an item, it must leave the item's location
            model += lpSum([routes[c][i][l] for l in LOCATIONS]) == item_per_courier[c][i]

def add_arrival_departure_constraints(model, routes, COURIERS, ITEMS, LOCATIONS):
    # Adds constraints to the model ensuring that if a courier arrives at a location for an item,
    # it must also leave that location.
    for c in COURIERS:
        for i in ITEMS:
            # Calculate the sum of routes arriving at item location
            courier_arrives = lpSum([routes[c][l][i] for l in LOCATIONS])
            # Calculate the sum of routes leaving from item location
            courier_leaves = lpSum([routes[c][i][l] for l in LOCATIONS])
            # If a courier arrives at an item location, it must also leave
            model += (1 - courier_arrives) + courier_leaves >= 1

def add_self_loop_constraints(model, routes, COURIERS, ITEMS):
    # Adds constraints to the model ensuring that couriers do not travel from a place to itself.
    for c in COURIERS:
        for i in ITEMS:
            # Couriers cannot travel from a node to itself
            model += routes[c][i][i] == 0

def add_distance_constraints(model, routes, D, distance_per_courier, COURIERS, LOCATIONS):
    # Adds constraints to the model ensuring that the calculated distance for each courier matches the sum of the distances for the routes they take.
    for c in COURIERS:
        # The total distance traveled by each courier must equal the sum of the distances for the routes they take
        model += lpSum([routes[c][i][j] * D[i][j] for i in LOCATIONS for j in LOCATIONS]) == distance_per_courier[c]
        
def add_max_distance_constraints(model, distance_per_courier, min_max_distance_per_courier, COURIERS):
    # Adds constraints to the model ensuring that the minimum maximum distance traveled by any courier is tracked.
    for c in COURIERS:
        # The minimum maximum distance must be greater than or equal to the distance traveled by each courier
        model += min_max_distance_per_courier >= distance_per_courier[c]
    # Add the objective function to minimize the maximum distance traveled
    model += min_max_distance_per_courier