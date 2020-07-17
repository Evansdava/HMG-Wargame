# Install base image for Python
FROM python:3.7-slim-buster

# Copy source code to the container
# In a folder named /app
COPY . /app

# Set working directory to execute commands properly
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Declare environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Expose the port Flask runs on
EXPOSE 5000

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0"]
