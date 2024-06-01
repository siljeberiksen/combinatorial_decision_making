import json
import re
import numpy as np

def process(data, number):
    if number <10:
        with open(f'Instances/inst0{number}.dat', 'r') as file:
            lines = file.readlines()
    else:
        with open(f'Instances/inst{number}.dat', 'r') as file:
            lines = file.readlines()
    
    # Process the input data
    m = int(lines[0].strip())
    n = int(lines[1].strip())
    print(data[0])
    raw_output = data[0]["output"]["raw"]
    routes_match = re.search(r'Routes: \[(.*?)\]', raw_output)
    if routes_match:
        routes_str = routes_match.group(1)
        routes_list = routes_str.split(', ')
        routes_bool_list = [route == 'true' for route in routes_list]
         # Reshape the 1D list into a 3D list
        three_d_list = np.array(routes_bool_list).reshape(m,n+1, n+1)
        next_distances=[]
        for two_d_list in three_d_list:
            print(two_d_list)
            next_distance = []
            for i in range(0,n):
                if two_d_list[n][i]==True:
                       next_distance.append(i+1)
                       not_at_end = True
                       while not_at_end:
                           for j in range(0,n+1):
                                if two_d_list[i][j] == True:
                                   if j == n:
                                       not_at_end = False
                                   else: 
                                       i=j
                                       next_distance.append(i+1)
            next_distances.append(next_distance)
            print(next_distance)
            print("\n\n\n\n\n\n")
        print(next_distances)
    else:
        print("Routes not found in the raw output.")
    max_distance = int(raw_output.split("Max Distance: ")[1].strip())

    time = data[0]["time"]
    status = 0
    for element in data:
        print("element", element)
        print(element["type"])
        if element["type"]=="status":
            status = element["status"]
    print("status", status)
    result_data = {
       "geocode": {
            "time": time/1000,
            "optimal": status == "OPTIMAL_SOLUTION",
            "obj": max_distance,
            "sol": next_distances
        }
    }


    with open(f"result/SAT/{number}.json", 'w') as output_file:
        json.dump(result_data, output_file, indent=4)



for k in range(2,3):
    print("k", k)
    with open(f'CP/results/inst{k}.json', 'r') as file:
        data = json.load(file)

    process(data, k)