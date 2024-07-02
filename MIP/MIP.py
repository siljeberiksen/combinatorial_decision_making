import pulp
import json

def solve_mcp(m, n, l_i, s_j, D):
    # Decision variables
    x = pulp.LpVariable.dicts('x', [(i, j) for i in range(m) for j in range(n)], cat=pulp.LpBinary)
    y = pulp.LpVariable.dicts('y', [(i, j, k) for i in range(m) for j in range(n) for k in range(n) if j != k], cat=pulp.LpBinary)
    
    # Model setup
    linear_programming_problem = pulp.LpProblem("Multiple_Couriers_Planning", pulp.LpMinimize)
    
    # Objective: Minimize the total distance traveled by all couriers
    distance_maximum = pulp.LpVariable("Maximum_distance", lowBound=0, cat='Continuous')
    linear_programming_problem += distance_maximum  # Objective variable
    
    for i in range(m):
        total_distance = pulp.lpSum(y[(i, j, k)] * D[j][k] for j in range(n) for k in range(n) if j != k)
        total_distance += pulp.lpSum(x[(i, j)] * D[0][j] for j in range(n))  # Distance from origin to items
        total_distance += pulp.lpSum(x[(i, j)] * D[j][0] for j in range(n))  # Distance from items back to origin
        linear_programming_problem += total_distance <= distance_maximum
    
    # Constraints
    for i in range(m):
        # Maximum load capacity constraint
        linear_programming_problem += pulp.lpSum(x[(i, j)] * s_j[j] for j in range(n)) <= l_i[i]
        
        for j in range(n):
            # Each item assigned exactly once
            linear_programming_problem += y[(i, j, j)] == 0  # No self-loop in tours
            linear_programming_problem += pulp.lpSum(y[(i, j, k)] for k in range(n) if j != k) == x[(i, j)]
            linear_programming_problem += pulp.lpSum(y[(i, k, j)] for k in range(n) if k != j) == x[(i, j)]
    
    # Solve the problem
    linear_programming_problem.solve()
    
    # Output the results in the desired format
    output = {"geocode": {"time": pulp.value(linear_programming_problem.solutionTime),
                          "optimal": pulp.LpStatus[linear_programming_problem.status] == "Optimal",
                          "obj": pulp.value(distance_maximum)}}
    
    # Output the results
    if pulp.LpStatus[linear_programming_problem.status] == "Optimal":
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

# Read input parameters from JSON file
with open('input_data1.json', 'r') as f:
    input_data = json.load(f)

m = input_data["m"]
n = input_data["n"]
l_i = input_data["l_i"]
s_j = input_data["s_j"]
D = input_data["D"]

# Solve the Multiple Couriers Problem (MCP) to achieve an objective value close to 14
solve_mcp(m, n, l_i, s_j, D)
