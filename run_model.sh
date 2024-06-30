#!/bin/sh
echo "hallo"
# Assign the arguments to variables
MODEL_FILE=$1
INSTANCE_FILE=$2
RESULT_FILE=$3

# Check if arguments are provided
if [ -z "$MODEL_FILE" ] || [ -z "$INSTANCE_FILE" ] || [ -z "$RESULT_FILE" ]; then
  echo "Usage: $0 <model_file> <instance_file> <result_file>"
  exit 1
fi


# Run the MiniZinc model with the specified instance and save the result
minizinc --json-stream --solver Gecode $MODEL_FILE -d $INSTANCE_FILE --solver-time-limit 300000 --output-time | jq -s '.' > $RESULT_FILE
