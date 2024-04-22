# Use an official lightweight Python image.
FROM python:3.8-slim

# Set the working directory in the container to /app.
WORKDIR /app

# Copy the current directory contents into the container at /app.
COPY . /app

# Install any needed packages specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container.
EXPOSE 5000

# Define environment variable.
# For example, if your app uses an environment variable for configuration.
ENV FLASK_ENV=production

# Run app.py when the container launches.
# Replace `app.py` with the entry point of your application.
CMD ["flask", "run", "--host=0.0.0.0"]
