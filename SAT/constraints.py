from z3 import *
from itertools import combinations
import numpy as np

# Code from the practical session with n-queen and sudoku problem

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



# Constraints definition

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


# Decision variables coherence.


def add_movement_constraints(solver, courier, location, courier_at_location_per_movement, routes,  max_roads):

    for c in courier:
        for r in max_roads:
            for i in location:
                for j in location:
                    # Add constraint: if courier is at location i at time r and at location j at time r+1, then the route between i and j is taken
                    solver.add(Implies(And(courier_at_location_per_movement[c][i][r],
                                           courier_at_location_per_movement[c][j][r + 1]),
                                       routes[c][i][j]))


# Minimize distance objective function.

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

