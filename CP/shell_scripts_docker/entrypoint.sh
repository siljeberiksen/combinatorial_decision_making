#!/bin/sh
TYPE=$1
if [ "$TYPE" = "single" ]; then
    # Assign the arguments to variables
    MODEL_FILE=$2
    INSTANCE_FILE=$3
    RESULT_FILE=$4
    SOLVER=$5
    exec ./CP/shell_scripts_docker/run_single_model.sh "$MODEL_FILE" "$INSTANCE_FILE" "$RESULT_FILE" "$SOLVER"
elif [ "$TYPE" = "all" ]; then
    exec ./CP/shell_scripts_docker/run_all_models.sh
else
    echo "Usage: $0 {single|all}"
    exit 1
fi