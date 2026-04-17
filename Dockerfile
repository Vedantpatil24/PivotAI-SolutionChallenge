# Use the official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose Port 8080 (Cloud Run standard)
EXPOSE 8080

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]