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

# Your application's entry point
CMD [ "python", "main.py" ]

FROM mysql:latest

ENV []