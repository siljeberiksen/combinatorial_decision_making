# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install PuLP package
RUN pip install --no-cache-dir pulp

# Make port 80 available to the world outside this container
EXPOSE 80

# Make script executable
RUN chmod +x MIP.py

# Command to run the Python script
CMD ["python", "./MIP.py"]

docker build -t  MIP.

docker run -v /path/to/local/data:/app/input_data -it MIP
