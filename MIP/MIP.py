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

# Decision variables
decisionVariables = pulp.LpVariable.dicts('x', [(i, j) for i in range(m) for j in range(n)], cat=pulp.LpBinary)
# x[i, j] is 1 if item j is assigned to courier i, otherwise 0

# Assigned sum of sizes for each courier
assignedSumOfSizesForEachCourier = [
    pulp.lpSum(decisionVariables[(i, j)] * s_j[j] for j in range(n)) for i in range(m)
]

# Distance traveled by each courier
distanceTraveledByEachCourier = [
    pulp.lpSum(decisionVariables[(i, j)] * D[0][j + 1] for j in range(n)) for i in range(m)
]

# Model setup
linearProgrammingProblem = pulp.LpProblem("Multiple Couriers Planning", pulp.LpMinimize)

# Constraints
for i in range(m):
    linearProgrammingProblem += assignedSumOfSizesForEachCourier[i] <= l_i[i]  # Max load capacity constraint

for j in range(n):
    linearProgrammingProblem += pulp.lpSum(decisionVariables[(i, j)] for i in range(m)) == 1  # Each item assigned exactly once

# Objective
distanceMaximum = pulp.LpVariable("Maximum_distance", lowBound=0, cat='Continuous')
linearProgrammingProblem += distanceMaximum  # Objective variable

for i in range(m):
    linearProgrammingProblem += distanceTraveledByEachCourier[i] <= distanceMaximum  # Minimize the maximum distance

# Solve the problem
linearProgrammingProblem.solve()

# Output the results in the desired format
output = {"geocode": {"time": pulp.value(linearProgrammingProblem.solutionTime), "optimal": pulp.LpStatus[linearProgrammingProblem.status] == "Optimal", "obj": pulp.value(distanceMaximum)}}

if pulp.LpStatus[linearProgrammingProblem.status] == "Optimal":
    result = [[] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if pulp.value(decisionVariables[(i, j)]) == 1:
                result[i].append(j + 1)  # Use 1-based indexing for consistency with CP output
    output["geocode"]["sol"] = result
else:
    output["geocode"]["sol"] = []

# Print the result in JSON format
print(json.dumps(output, indent=4))
