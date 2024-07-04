import pulp
import json

# Read input parameters from JSON file
with open('input_data3.json', 'r') as f:
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
distance = [pulp.lpSum([x[i, j] * D[0][j + 1] for j in range(n)]) for i in range(m)]  # From depot (index 0) to items
max_distance = pulp.LpVariable("max_distance", lowBound=0, cat='Continuous')

# Constraints
for i in range(m):
    # Maximum load capacity constraint
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] * s_j[j] for j in range(n)) <= l_i[i]

for j in range(n):
    # Each item assigned exactly once
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] for i in range(m)) == 1




# Minimize the maximum distance
linearProgrammingProblem += distanceMaximum

# Solve the problem
linearProgrammingProblem.solve()

# Output the results in the desired format
output = {
    "geocode": {
        "time": pulp.value(linearProgrammingProblem.solutionTime),
        "optimal": pulp.LpStatus[linearProgrammingProblem.status] == "Optimal",
        "obj": pulp.value(distanceMaximum)
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
