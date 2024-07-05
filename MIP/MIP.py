import pulp
import json

# Read input parameters from JSON file
with open('input_data1.json', 'r') as f:
    input_data = json.load(f)

m = input_data["m"]
n = input_data["n"]
l_i = input_data["l_i"]
s_j = input_data["s_j"]
D = input_data["D"]

# Model setup
linearProgrammingProblem = pulp.LpProblem("Multiple_Couriers_Planning", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts('x', [(i, j) for i in range(m) for j in range(n)], cat='Binary')
y = pulp.LpVariable.dicts('y', [(i, j, k) for i in range(m) for j in range(n+1) for k in range(n+1)], cat='Binary')

# Constraints
for i in range(m):
    # Maximum load capacity constraint
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] * s_j[j] for j in range(n)) <= l_i[i]

for j in range(n):
    # Each item assigned exactly once
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] for i in range(m)) == 1

# Route continuity constraints
for i in range(m):
    # Depart from depot
    linearProgrammingProblem += pulp.lpSum(y[(i, 0, j)] for j in range(1, n+1)) == 1
    # Return to depot
    linearProgrammingProblem += pulp.lpSum(y[(i, j, 0)] for j in range(1, n+1)) == 1
    
    for j in range(1, n+1):
        # Flow conservation
        linearProgrammingProblem += pulp.lpSum(y[(i, k, j)] for k in range(n+1) if k != j) == \
                                    pulp.lpSum(y[(i, j, k)] for k in range(n+1) if k != j)
        # Link x and y
        if j <= n:
            linearProgrammingProblem += pulp.lpSum(y[(i, k, j)] for k in range(n+1) if k != j) == x[(i, j-1)]

# Define the max distance variable
maxTraveledDistance = pulp.LpVariable("maxTraveledDistance", lowBound=0, cat='Continuous')

# Distance calculation and max distance constraint
for i in range(m):
    courier_distance = pulp.lpSum(y[(i, j, k)] * D[j][k] for j in range(n+1) for k in range(n+1) if j != k)
    linearProgrammingProblem += courier_distance <= maxTraveledDistance

# Objective
linearProgrammingProblem += maxTraveledDistance

# Solve the problem
linearProgrammingProblem.solve()

print(f"Solver status: {pulp.LpStatus[linearProgrammingProblem.status]}")
print(f"Objective value: {pulp.value(linearProgrammingProblem.objective)}")

# Check if any variables are None
none_vars = [(i, j, k) for i in range(m) for j in range(n+1) for k in range(n+1) if pulp.value(y[(i, j, k)]) is None]
if none_vars:
    print("Warning: Some y variables are None:")
    for var in none_vars[:10]:  # Print first 10 None variables
        print(var)
    if len(none_vars) > 10:
        print(f"... and {len(none_vars) - 10} more")

# Output the results in the desired format
output = {
    "geocode": {
        "time": pulp.value(linearProgrammingProblem.solutionTime),
        "optimal": pulp.LpStatus[linearProgrammingProblem.status] == "Optimal",
        "obj": pulp.value(maxTraveledDistance)
    }
}

# Output the results
if pulp.LpStatus[linearProgrammingProblem.status] == "Optimal":
    result = [[] for _ in range(m)]
    for i in range(m):
        current = 0  # Start from the depot
        route = [current]
        while True:
            next_stop = None
            for j in range(1, n+1):
                y_value = pulp.value(y[(i, current, j)])
                if y_value is not None and y_value > 0.5:
                    next_stop = j
                    break
            if next_stop is None:
                break
            route.append(next_stop)
            result[i].append(next_stop - 1)  # Subtract 1 to match the original 0-based indexing
            current = next_stop
        print(f"Courier {i} route: {route}")
    output["geocode"]["sol"] = result
else:
    output["geocode"]["sol"] = []

# Print the result in JSON format
print(json.dumps(output, indent=4))
