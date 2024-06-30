# FROM minizinc/minizinc:latest

# WORKDIR /src

# # Copy the script into the container
# COPY . .

# #RUN apt-get install python3
# RUN apt-get update && apt-get install -y jq


# CMD minizinc --json-stream --solver Gecode CP/eksamen.mzn -d Instances_dzn/inst02.dzn --solver-time-limit 300000 --output-time | jq -s '.' > CP/results/inst2.json

# ## %% python3 main.py

# Use the official MiniZinc image from the Docker Hub
FROM minizinc/minizinc:latest

# Install jq for JSON processing
RUN apt-get update && apt-get install -y jq

# Set the working directory
WORKDIR /src

# Copy all the files into the container
COPY . .

# Make sure the run_model.sh script is executable
RUN chmod +x ./run_all_models.sh
RUN chmod +x ./run_model.sh
RUN chmod +x ./CP


# Define the entry point script
ENTRYPOINT ["./run_all_models.sh"]