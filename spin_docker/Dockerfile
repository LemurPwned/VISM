# Get Python 3.6.3
FROM python:3.6.3-slim

# Set container working dir to /app
WORKDIR /spindocker

# Copy current directory contents into the container at /app
ADD . /spindocker
ADD requirements.txt /spindocker/requirements.txt

# Download git
RUN  apt-get update && apt-get install -y git

# Install requirements from requirements.txt file
RUN pip install -r /spindocker/requirements.txt

# Download github repository
RUN git clone https://github.com/LemurPwned/spintronics-visual.git

# Make port 5000 avalable to the world outside container
EXPOSE 5000

# Define environment variable
ENV NAME SpinDocker

# Run application
CMD ["python", "/spindocker/spintronics-visual/main.py"]
