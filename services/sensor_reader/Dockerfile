# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY ./services/sensor_reader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the build context
# Note: We copy the whole project context, then select what we need.
COPY ./services/sensor_reader /app

# Command to run the application using the module execution flag
# This makes the "red imports" problem go away inside Docker.
CMD ["python", "-m", "src.main"]