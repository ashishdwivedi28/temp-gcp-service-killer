# Python image to use.
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file.
COPY requirements.txt .

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Run the application.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
