# Use a slim Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port Django runs on
EXPOSE 8000

# Run Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]   