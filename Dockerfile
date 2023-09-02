# Use an official Python runtime as a parent image
FROM python:latest

# Set environment variables for database connection
ENV DB_HOST=db_host
ENV DB_PORT=3306
ENV DB_NAME=your_database_name
ENV DB_USER=your_database_user
ENV DB_PASSWORD=your_database_password

# Set the working directory in the container
WORKDIR /stellarbot

# Copy the requirements file into the container at /app
COPY requirements.txt /stellarbot/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /stellarbot/

# Expose port for your application (change it to your application's port)
EXPOSE 8080

# Define the command to run your application


CMD ["python", "main.py"]

#no display name and no $DISPLAY environment variable
