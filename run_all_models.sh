#!/bin/bash

MODELS_DIR="./CP"
INSTANCES_DIR="./Instances_dzn"
RESULTS_DIR="./CP/results"

# Ensure results directory exists
mkdir -p $RESULTS_DIR

# Define an array of solvers
SOLVERS=("Gecode" "Chuffed")
for solver in $SOLVERS; do
  for MODEL in "$MODELS_DIR"/*.mzn; do
    # Check if there are any .mzn files to process
    echo "Processing $MODEL" 
    for INSTANCE in $INSTANCES_DIR/*.dzn; do
      echo $INSTANCE
      MODEL_NAME=$(basename $MODEL .mzn)
      INSTANCE_NAME=$(basename $INSTANCE .dzn)
      RESULT_FILE="$RESULTS_DIR/${MODEL_NAME}/${INSTANCE_NAME}.json"

      # Run the model on the instance and save the result
      ./run_model.sh $MODEL $INSTANCE $RESULT_FILE $solver
    done
  done
done