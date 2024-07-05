import sys
import os
from solver_module import MCP

def read_instance_data(file_path):
    # Read the data and extract the variables.
    with open(file_path, 'r') as file:
        lines = file.readlines()
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        li = list(map(int, lines[2].strip().split()))
        sj = list(map(int, lines[3].strip().split()))
        D = [list(map(int, line.strip().split())) for line in lines[4:]]
    return m, n, li, sj, D

# Read instance data from a file and run the MCP function with the extracted parameters.
def process_instance(file_path, time_limit=300):
    
    # Extract instance name from file path
    instance_name = file_path.split('/')[-1].split('.')[0]
    
    # Read instance data from file
    m, n, li, sj, D = read_instance_data(file_path)
    
    # Call MCP with extracted parameters
    return MCP(m, n, li, sj, D, instance_name, time_limit)


if __name__ == '__main__':
    import multiprocessing as mp
    mp.freeze_support()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <instance_number>")
        sys.exit(1)

    instance_number = sys.argv[1]
    file_path = f'Instances/inst{instance_number}.dat'
    
    if not os.path.exists(file_path):
        print(f"Instance file {file_path} does not exist.")
        sys.exit(1)
    
    result = process_instance(file_path)
    print(result)