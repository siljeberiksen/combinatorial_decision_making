#!/bin/bash

# Loop through versions 1 to 22
for version in {1..22}; do
    echo "Running version $version..."
    minizinc --json-stream --solver Gecode CP/eksamen.mzn -d Instances_dzn/inst${version}.dzn --solver-time-limit 300000 --output-time | jq -s '.' > CP/results/inst${version}.json
    echo "Version $version done."
done

echo "All versions processed."