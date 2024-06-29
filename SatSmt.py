import z3

# Number of couriers and items
m = 3
n = 7

# Maximum load size of each courier i
l_i = [15, 10, 7]

# Size of each item
s_j = [3, 2, 6, 8, 5, 4, 4]

# Distance matrix
D = [
    [0, 3, 3, 6, 5, 6, 6, 2],
    [3, 0, 4, 3, 4, 7, 7, 3],
    [3, 4, 0, 7, 6, 3, 5, 3],
    [6, 3, 7, 0, 3, 6, 6, 4],
    [5, 4, 6, 3, 0, 3, 3, 3],
    [6, 7, 3, 6, 3, 0, 2, 4],
    [6, 7, 5, 6, 3, 2, 0, 4],
    [2, 3, 3, 4, 3, 4, 4, 0]
]

# Reached points of items
reachedPointsOfItems = [1, 2, 3, 4, 5, 6, 7]

# Initialize the Z3 optimizer
constraintsSolver = z3.Optimize()

# Decision variables
decisionVariables = [[z3.Bool(f'x_{i}_{j}') for j in range(n)] for i in range(m)]

# Constraints for max load capacity
for i in range(m):
    constraintsSolver.add(z3.Sum([z3.If(decisionVariables[i][j], s_j[j], 0) for j in range(n)]) <= l_i[i])

# Constraints to ensure each item is assigned exactly once
for j in range(n):
    constraintsSolver.add(z3.Sum([z3.If(decisionVariables[i][j], 1, 0) for i in range(m)]) == 1)

# Distance traveled by each courier
distanceTraveledByEachCourier = []
for i in range(m):
    totalDistance = z3.Sum([z3.If(decisionVariables[i][j], D[0][reachedPointsOfItems[j]], 0) for j in range(n)])
    distanceTraveledByEachCourier.append(totalDistance)

# Minimize the maximum distance
distanceMax = z3.Real('distanceMax')
for dist in distanceTraveledByEachCourier:
    constraintsSolver.add(dist <= distanceMax)
constraintsSolver.minimize(distanceMax)

# Check the solution
if constraintsSolver.check() == z3.sat:
    model = constraintsSolver.model()
    result = [[] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if model.evaluate(decisionVariables[i][j]):
                result[i].append(j)
    print(f"Maximum distance: {model.evaluate(distanceMax)}, Result: {result}")
else:
    print("No optimal solution found.")
