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
# Install necessary tools
RUN apt-get update && apt-get install -y jq python3 python3-pip python3-venv

# Set the working directory
WORKDIR /src

# Copy all the files into the container
COPY . .

# Make sure the run_model.sh script is executable
RUN chmod +x ./run_all_models.sh
RUN chmod +x ./run_model.sh
RUN chmod +x ./run_single_model.sh
RUN chmod +x ./CP
RUN chmod +x ./result
RUN chmod +x ./entrypoint.sh

# Create and activate a virtual environment, then install dependencies
RUN python3 -m venv venv
RUN . venv/bin/activate && pip install -r requirements_cp.txt

# # Define the entry point script
ENTRYPOINT ["./entrypoint.sh"]

# Default command: provide help information
CMD ["sh", "-c", "echo 'Usage: docker run --rm -v \${PWD}/CP/results:/src/CP/results cp <script> <model_file> <instance_file> <result_file> <solver>'; echo 'Example: docker run --rm -v \${PWD}/CP/results:/src/CP/results -v \${PWD}/Instances_dzn:/src/Instances_dzn cp ./run_single_model.sh /src/CP/nsb_dwd_im.mzn /src/Instances_dzn/inst01.dzn /src/CP/results/nsb_dwd_im/Gecode/inst01.json Gecode'"]
