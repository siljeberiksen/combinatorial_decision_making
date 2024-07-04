# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files into the container
COPY MIP.py input_data1.json ./

# Install PuLP package
RUN pip install --no-cache-dir pulp

# Make script executable
RUN chmod +x MIP.py

# Command to run the Python script
CMD ["python", "./MIP.py"]

docker build -t  MIP.

docker run -v /path/to/local/data:/app/input_data -it MIP
