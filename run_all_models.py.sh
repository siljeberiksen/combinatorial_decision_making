#!/bin/bash

MODELS_DIR="./models"
INSTANCES_DIR="./instances"
RESULTS_DIR="./results"

# Ensure results directory exists
mkdir -p $RESULTS_DIR

# Iterate over all models and instances
for MODEL in $MODELS_DIR/*.mzn; do
  for INSTANCE in $INSTANCES_DIR/*.dzn; do
    MODEL_NAME=$(basename $MODEL .mzn)
    INSTANCE_NAME=$(basename $INSTANCE .dzn)
    RESULT_FILE="$RESULTS_DIR/${MODEL_NAME}_${INSTANCE_NAME}.json"

    # Run the model on the instance and save the result
    ./run_model.sh $MODEL $INSTANCE $RESULT_FILE
  done
done