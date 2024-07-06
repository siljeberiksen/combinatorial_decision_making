#!/bin/bash

MODELS_DIR="./CP"
INSTANCES_DIR="./Instances_dzn"
RESULTS_DIR="./CP/results"

# Ensure results directory exists
mkdir -p $RESULTS_DIR

# Define an array of solvers
SOLVERS=("Gecode" "Chuffed")
# for solver in "${SOLVERS[@]}"; do
for solver in "${SOLVERS[@]}"; do
  echo solver $solver
  for MODEL in "$MODELS_DIR"/*.mzn; do
  #for MODEL in "./CP/sb_dwd_ir.mzn"; do
    # Check if there are any .mzn files to process
    echo "Processing $MODEL" 
    for INSTANCE in $INSTANCES_DIR/*.dzn; do
      MODEL_NAME=$(basename $MODEL .mzn)
      INSTANCE_NAME=$(basename $INSTANCE .dzn)
      RESULT_FILE="$RESULTS_DIR/${MODEL_NAME}/${solver}/${INSTANCE_NAME}.json"

      # Run the model on the instance and save the result
      ./run_model.sh $MODEL $INSTANCE $RESULT_FILE $solver
    done
  done
done

. venv/bin/activate && python3 post_processing.py