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
# x[i, j] is 1 if item j is assigned to courier i, otherwise 0

# Distance calculation
# Initialize the distance list for each courier
distance = []

# Calculate the distance for each courier
for i in range(m):
    # Sum of distances from the depot (index 0) to each item assigned to courier i
    courier_distance = pulp.lpSum([x[i, j] * D[0][j + 1] for j in range(n)])

    # Append the calculated distance to the distance list
    distance.append(courier_distance)

# Define the maximum distance variable
max_distance = pulp.LpVariable("max_distance", lowBound=0, cat='Continuous')

# Detailed comments explaining the distance calculation steps:
# 1. We initialize an empty list called 'distance' which will hold the total distance traveled by each courier.
# 2. We loop over each courier (from 0 to m-1) to calculate their individual distances.
# 3. For each courier, we calculate the sum of distances from the depot (index 0) to each item they are assigned to.
# 4. The assignment of items to couriers is determined by the decision variables 'x[i, j]', which are binary (0 or 1).
# 5. We use the distance matrix 'D' to get the distance from the depot to each item (j+1 because depot is index 0).
# 6. The calculated distance for each courier is then appended to the 'distance' list.
# 7. Finally, we define a new variable 'max_distance' which will be used to minimize the maximum distance any courier travels.

# Note: In this problem, we assume that the couriers start from the depot, visit their assigned items, and return to the depot.
# Hence, the distance calculation here only includes the outgoing trip from the depot to each assigned item.


# Constraints
for i in range(m):
    # Maximum load capacity constraint
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] * s_j[j] for j in range(n)) <= l_i[i], f"Max_load_constraint_{i}"

for j in range(n):
    # Each item assigned exactly once
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] for i in range(m)) == 1, f"One_courier_per_item_{j}"

# Objective: Minimize the maximum distance traveled by any courier
linearProgrammingProblem += max_distance
for i in range(m):
    linearProgrammingProblem += distance[i] <= max_distance, f"Max_distance_constraint_{i}"

# Solve the problem
linearProgrammingProblem.solve()

# Output the results in the desired format
output = {
    "geocode": {
        "time": pulp.value(linearProgrammingProblem.solutionTime),
        "optimal": pulp.LpStatus[linearProgrammingProblem.status] == "Optimal",
        "obj": pulp.value(max_distance)
    }
}

# Output the results
if pulp.LpStatus[linearProgrammingProblem.status] == "Optimal":
    result = [[] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if pulp.value(x[(i, j)]) == 1:
                result[i].append(j)
    output["geocode"]["sol"] = result
else:
    output["geocode"]["sol"] = []

# Print the result in JSON format
print(json.dumps(output, indent=4))
