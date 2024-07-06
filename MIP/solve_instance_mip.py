import sys
import os
from solver_module_mip import *

# Wrapper function to call the target function and store the result in a dictionary
def wrapper(func, args, return_dict):
    result = func(*args)
    return_dict['result'] = result

# Function to run a given function with a timeout
def run_with_timeout(func, args, timeout, instance_name):
    manager = multiprocessing.Manager()  # Create a manager to handle shared data between processes
    return_dict = manager.dict()  # Create a shared dictionary to store the result
    p = multiprocessing.Process(target=wrapper, args=(func, args, return_dict))  # Create a new process to run the function
    p.start()  # Start the process
    p.join(timeout)  # Wait for the process to complete or timeout

    if p.is_alive():  # If the process is still running after the timeout
        p.terminate()  # Terminate the process
        p.join()  # Wait for the process to terminate
        print("Timeout: Function exceeded time limit")
        save_results(None, None, timeout, False, instance_name)  # Save results indicating timeout
        return None, False, None, timeout  # Return default values indicating timeout

    return return_dict.get('result', (None, False, None, timeout))  # Return the result or default values if not found

# Function to read instance data from a file
def read_instance_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        li = list(map(int, lines[2].strip().split()))
        sj = list(map(int, lines[3].strip().split()))
        D = [list(map(int, line.strip().split())) for line in lines[4:]]
    return m, n, li, sj, D

# Function to process an instance file with a given time limit
def process_instance(file_path, time_limit=300):
    instance_name = file_path.split('/')[-1].split('.')[0]  # Extract instance name from file path
    m, n, li, sj, D = read_instance_data(file_path)  # Read instance data from file
    return run_with_timeout(MCP_MIP_PULP, (m, n, li, sj, D, instance_name), time_limit, instance_name)  # Run the function with timeout

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