#!/bin/sh

# Example usage: ./run_single_model.sh CP/model.mzn Instances_dzn/inst01.dzn CP/results/inst01.json Gecode

# Assign the arguments to variables
MODEL_FILE=$1
INSTANCE_FILE=$2
RESULT_FILE=$3
SOLVER=$4

. venv/bin/activate && python3 CP/process_files/pre_process_files.py

# Call run_model.sh with the provided arguments
./CP/shell_scripts_docker/run_model.sh $MODEL_FILE $INSTANCE_FILE $RESULT_FILE $SOLVER
# Call the post-processing script
# Activate the virtual environment and run the post-processing script
. venv/bin/activate && python3 CP/process_files/post_processing.py
