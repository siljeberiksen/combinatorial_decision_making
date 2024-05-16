import json
import re
import numpy as np

def process(data):
    raw_output = data[0]["output"]["raw"]
    routes_match = re.search(r'Routes: \[(.*?)\]', raw_output)
    if routes_match:
        routes_str = routes_match.group(1)
        routes_list = routes_str.split(', ')
        routes_bool_list = [route == 'true' for route in routes_list]
         # Reshape the 1D list into a 3D list
        three_d_list = np.array(routes_bool_list).reshape(6,10, 10)
        next_distances=[]
        for two_d_list in three_d_list:
            next_distance = []
            for i in range(0,6):
                for j in range(0,7):
                    if two_d_list[i][j]==True:
                        next_distance.append(i+1)
            next_distances.append(next_distance)
        print(next_distances)
    else:
        print("Routes not found in the raw output.")
    max_distance = int(raw_output.split("Max Distance: ")[1].strip())

    time = data[0]["time"]
    status = False
    for element in data:
        if element["type"]==status:
            status = element["status"]
    
    result_data = {
       "geocode": {
            "time": time,
            "optimal": status == "OPTIMAL_SOLUTION",
            "obj": max_distance,
            "sol": next_distances
        }
    }


    with open("result/SAT/1.json", 'w') as output_file:
        json.dump(result_data, output_file, indent=4)




with open("CP/results/inst2.json", 'r') as file:
    data = json.load(file)

process(data)