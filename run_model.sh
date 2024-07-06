#!/bin/sh
# Assign the arguments to variables
MODEL_FILE=$2
INSTANCE_FILE=$3
RESULT_FILE=$4
SOLVER=$5
echo "Halo"
echo $MODEL_FILE
echo $INSTANCE_FILE
echo $RESULT_FILE
echo $SOLVER

# Check if arguments are provided
if [ -z "$MODEL_FILE" ] || [ -z "$INSTANCE_FILE" ] || [ -z "$RESULT_FILE" ]; then
  echo "Usage: $0 <model_file> <instance_file> <result_file>"
  exit 1
fi
#CP/CP.mzn
#Instances_dzn/inst02.dzn
#CP/results/insttest2.json

# Run the MiniZinc model with the specified instance and save the result
minizinc --json-stream --solver $SOLVER $MODEL_FILE -d $INSTANCE_FILE --solver-time-limit 290000 --output-time | jq -s '.' > $RESULT_FILE   
