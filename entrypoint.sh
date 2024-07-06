#!/bin/sh
if [ "$1" = "single" ]; then
    exec ./run_single_model.sh
elif [ "$1" = "all" ]; then
    exec ./run_all_models.sh
else
    echo "Usage: $0 {single|all}"
    exit 1
fi