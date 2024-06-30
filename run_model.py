from datetime import timedelta
import sys
import json
import os
from minizinc import Instance, Model, Solver

# Usage: python run_model.py <model_file> <instance_file> <result_file>
if len(sys.argv) != 4:
    print("Usage: python run_model.py <model_file> <instance_file> <result_file>")
    sys.exit(1)

model_file = sys.argv[1]
instance_file = sys.argv[2]
result_file = sys.argv[3]

# Check if the model file exists
if not os.path.exists(model_file):
    print(f"Error: Model file '{model_file}' does not exist.")
    sys.exit(1)

# Check if the instance file exists
if not os.path.exists(instance_file):
    print(f"Error: Instance file '{instance_file}' does not exist.")
    sys.exit(1)

try:
    # Load the MiniZinc model
    model = Model(model_file)

    # Load the instance data
    with open(instance_file, 'r') as f:
        instance_data = f.read()

    # Add the instance data to the model
    model.add_string(instance_data)

    # Find the MiniZinc solver configuration
    gecode = Solver.lookup("gecode")

    # Create an Instance of the model for the solver
    instance = Instance(gecode, model)

    # Set a time limit for the solver (300 seconds)
    result = instance.solve(timeout=timedelta(seconds=300))
    
    print(result)
    # Save the results to a JSON file
    # with open(result_file, 'w') as f:
    #     json.dump(result, f)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
