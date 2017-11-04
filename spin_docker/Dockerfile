# Get Python 3.6.3
FROM python:3.6.3-slim

# Set container working dir to /app
WORKDIR /app

# Copy current directory contents into the container at /app
ADD . /app
ADD requirements.txt /app/requirements.txt

# Install requirements from requirements.txt file
RUN pip install -r /app/requirements.txt

# Make port 5000 avalable to the world outside container
EXPOSE 5000

# Define environment variable
ENV NAME World
