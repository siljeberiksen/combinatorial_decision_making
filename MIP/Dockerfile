# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install PuLP package
RUN pip install --no-cache-dir pulp

# Make script executable
# Uncomment the following line if MIP.py needs to be executable
# RUN chmod +x MIP.py

# Command to run the Python script
CMD ["python", "./MIP.py"]

# Expose port 80 (if your script inside the container listens on this port)
# EXPOSE 80

# The following commands are for reference, not part of the Dockerfile
# They should be executed in your terminal outside of the Dockerfile
# Build the Docker image
# docker build -t combinatorialproject .

# Run the Docker container, mount 'res' directory from host to container
# docker run -v $(pwd)/res:/app/res combinatorialproject
