import pulp
import json

# Input parameters
m = 3  # number of couriers
n = 7  # number of items
l_i = [15, 10, 7]  # maximum load size of each courier i
s_j = [3, 2, 6, 8, 5, 4, 4]  # size of each item
D = [
    [0, 3, 3, 6, 5, 6, 6, 2],
    [3, 0, 4, 3, 4, 7, 7, 3],
    [3, 4, 0, 7, 6, 3, 5, 3],
    [6, 3, 7, 0, 3, 6, 6, 4],
    [5, 4, 6, 3, 0, 3, 3, 3],
    [6, 7, 3, 6, 3, 0, 2, 4],
    [6, 7, 5, 6, 3, 2, 0, 4],
    [2, 3, 3, 4, 3, 4, 4, 0]
]  # distance matrix

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
