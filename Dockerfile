# Use the official lightweight Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for SQLite and general tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Expose the port Streamlit runs on (8080 is standard for Cloud Run)
EXPOSE 8080

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]