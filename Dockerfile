# Use a base image with Python and tk (for tkinter)
FROM python:3.11-slim

# Set the working directory
WORKDIR /stellarbot

# Install tk and other dependencies
RUN apt-get update && apt-get install -y tk pkg-config 


# Copy the requirements file
COPY requirements.txt .

# Install pip requirements
RUN python -m pip install -r requirements.txt

# Copy the rest of your application code
COPY . /stellarbot/




# Use a base image with Python

# Install tkinter (tk) package and Xvfb (virtual display)
RUN apt-get update && apt-get install -y python3-tk xvfb


# Set up the virtual display
ENV DISPLAY=:99
# Your application's entry point
EXPOSE  8090

# Start Xvfb and run the Python script
CMD [ "Xvfb :99 -screen 0 1280x1024x16 &", "python", "main.py" ]