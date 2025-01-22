# Use the official Python image
FROM python:3.10-slim

# Update pip
RUN pip install --upgrade pip

# Install the dependencies 
RUN pip install Flask flask-cors requests

# Copy the Flask app code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Expose the port the app will run on
EXPOSE 8080

# Run the Flask app
CMD ["python", "back-end.py"]
