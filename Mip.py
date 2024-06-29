import pulp

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
reachedPointsOfItems = [1, 2, 3, 4, 5, 6, 7]  # example points for items, adjust as needed

# Decision variables
decisionVariables = pulp.LpVariable.dicts('x', [(i, j) for i in range(m) for j in range(n)], cat=pulp.LpBinary)
# x[i, j] is 1 if item j is assigned to courier i, otherwise 0

# Assigned sum of sizes for each courier
assignedSumOfSizesForEachCourier = []
for i in range(m):
    assignedSumOfSizesForEachCourier.append(
        pulp.lpSum(decisionVariables[(i, j)] * s_j[j] for j in range(n))
    )

# Distance traveled by each courier
distanceTraveledByEachCourier = []
for i in range(m):
    currentStartingPoint = 0  # Assuming starting point is 0 (o)
    temporyList2 = []
    for j in range(n):
        temporyList2.append(
            decisionVariables[(i, j)] * D[currentStartingPoint][reachedPointsOfItems[j]]
        )
        currentStartingPoint = reachedPointsOfItems[j]  # Update starting point
    distanceTraveledByEachCourier.append(pulp.lpSum(temporyList2))

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

# Output the results
if pulp.LpStatus[linearProgrammingProblem.status] == "Optimal":
    result = [[] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if pulp.value(decisionVariables[(i, j)]) == 1:
                result[i].append(j)
    print(f"Maximum distance: {pulp.value(distanceMaximum)}, Result: {result}")
else:
    print("No optimal solution found.")
