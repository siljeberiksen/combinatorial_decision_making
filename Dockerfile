FROM minizinc/minizinc:latest

WORKDIR /src

# Copy the script into the container
COPY . .

#RUN apt-get install python3
RUN apt-get update && apt-get install -y jq


CMD minizinc --json-stream --solver Gecode CP/eksamen.mzn -d Instances_dzn/inst02.dzn --solver-time-limit 300000 --output-time | jq -s '.' > CP/results/inst2.json

## %% python3 main.py