from z3 import *

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
binVar = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(m)]
# binVar[i][j] is True if item j is assigned to courier i, False otherwise

# Calculate total item size carried by each courier
totalItemSizeEachCourierList = []
for i in range(m):
    totalItemSizeEachCourier = Sum([If(binVar[i][j], s_j[j], 0) for j in range(n)])
    totalItemSizeEachCourierList.append(totalItemSizeEachCourier)

# Calculate total distance traveled by each courier
listTotalDistanceEachCourier = []
for i in range(m):
    t_i = Sum([If(binVar[i][j], D[0][j], 0) for j in range(n)])  # Assuming startingPoint is 0 (o)
    listTotalDistanceEachCourier.append(t_i)

# Constraints setup
constraintsSolver = Solver()
for i in range(m):
    constraintsSolver.add(totalItemSizeEachCourierList[i] <= l_i[i])  # Load capacity constraint

for j in range(n):
    constraintsSolver.add(Sum([If(binVar[i][j], 1, 0) for i in range(m)]) == 1)  # Each item assigned exactly once

# Objective to minimize the maximum distance traveled by any courier
distanceMax = Int('distanceMax')
constraintsSolver.add(distanceMax == Max(listTotalDistanceEachCourier))
constraintsSolver.minimize(distanceMax)

# Solve and obtain solution
if constraintsSolver.check() == sat:
    solModel = constraintsSolver.model()
    matrixAssigning = [[] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if is_true(solModel[binVar[i][j]]):
                matrixAssigning[i].append(j)
    solution = matrixAssigning
    print(f"Maximum distance: {solModel[distanceMax]}, solution: {solution}")
else:
    print("There is no solution")
