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
x = pulp.LpVariable.dicts('x', [(i, j) for i in range(m) for j in range(n)], cat=pulp.LpBinary)
y = pulp.LpVariable.dicts('y', [(i, j, k) for i in range(m) for j in range(n) for k in range(n) if j != k], cat=pulp.LpBinary)
# x[i, j] is 1 if item j is assigned to courier i, otherwise 0
# y[i, j, k] is 1 if courier i travels from item j to item k, otherwise 0

# Model setup
linearProgrammingProblem = pulp.LpProblem("Multiple_Couriers_Planning", pulp.LpMinimize)

# Constraints
for i in range(m):
    # Maximum load capacity constraint
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] * s_j[j] for j in range(n)) <= l_i[i]

for j in range(n):
    # Each item assigned exactly once
    linearProgrammingProblem += pulp.lpSum(x[(i, j)] for i in range(m)) == 1

# Subtour elimination constraints
for i in range(m):
    for j in range(n):
        linearProgrammingProblem += pulp.lpSum(y[(i, j, k)] for k in range(n) if j != k) == x[(i, j)]
        linearProgrammingProblem += pulp.lpSum(y[(i, k, j)] for k in range(n) if k != j) == x[(i, j)]

# Objective: Minimize the maximum distance traveled by any courier
distanceMaximum = pulp.LpVariable("Maximum_distance", lowBound=0, cat='Continuous')
for i in range(m):
    total_distance = pulp.lpSum(y[(i, j, k)] * D[j + 1][k + 1] for j in range(n) for k in range(n) if j != k)
    total_distance += pulp.lpSum(x[(i, j)] * D[0][j + 1] for j in range(n))  # Distance from origin to first item
    total_distance += pulp.lpSum(x[(i, j)] * D[j + 1][0] for j in range(n))  # Distance from last item back to origin
    linearProgrammingProblem += total_distance <= distanceMaximum

# Minimize the maximum distance
linearProgrammingProblem += distanceMaximum

# Solve the problem
linearProgrammingProblem.solve()

# Output the results in the desired format
output = {"geocode": {"time": pulp.value(linearProgrammingProblem.solutionTime),
                      "optimal": pulp.LpStatus[linearProgrammingProblem.status] == "Optimal",
                      "obj": pulp.value(distanceMaximum)}}

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
