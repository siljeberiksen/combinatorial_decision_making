import json
import re
import numpy as np

def process(data, filename):
    instance = filename.replace('.json', '')
    with open(f'Instances/{instance}.dat', 'r') as file:
          lines = file.readlines()
    
    m = int(lines[0].strip())
    n = int(lines[1].strip())
    if isinstance(data, list) and len(data) > 0 and "output" in data[0] and "raw" in data[0]["output"]:
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
        else:
            print("Routes not found in the raw output.")
        max_distance = int(raw_output.split("Max Distance: ")[1].strip())
    else: 
        max_distance = None
        next_distances = None

    if isinstance(data, list) and len(data) > 0 and "time" in data[0]:
        time = data[0]["time"]
    else:
        time=30000
    status = 0
    for element in data:
        if element["type"]=="status":
            status = element["status"]
    if status != "OPTIMAL_SOLUTION":
        time = 300000
    result_data = {
            "time": time/1000,
            "optimal": status == "OPTIMAL_SOLUTION",
            "obj": max_distance,
            "sol": next_distances
        }

    return result_data



# Define the directory containing the JSON files
import os

# Define the directory path
directory_path = './CP/results/'

# Initialize a list to hold the subdirectory names
subdirectories = []

# Iterate over each item in the directory
for item in ["sb_dwd_im", "nsb_dwd_im", "sb_dwd_ir", "nsb_dwd_ir"]:
    item_path = os.path.join(directory_path, item)
    # Check if the item is a directory
    if os.path.isdir(item_path):
        subdirectories.append(item)
    


# Initialize the dictionary
results = {}
for folder in subdirectories:
    for solver in ["Gecode", "Chuffed"]:
        for filename in os.listdir(directory_path + folder + "/"+ solver):
            if filename.endswith(".json"):
                with open(directory_path + folder + "/" + solver + "/" + filename, 'r') as file:
                    data = json.load(file)
                    result = process(data, filename)
                    if  filename.replace('.json', '') not in results:
                        results[filename.replace('.json', '')] =  {}
                    # Update the nested dictionary
                    results[filename.replace('.json', '')][folder+ "_" + solver]= result

for key, value in results.items():
      # Use regular expression to extract the number
    number = re.findall(r'\d+', key)

        # Convert to integer
    extracted_number = int(number[0]) if number else None

    with open(f"result/CP/{extracted_number}.json", 'w') as output_file:
        json.dump(value, output_file, indent=4)

    print("Files saved")