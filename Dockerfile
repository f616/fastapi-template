# Dockerfile
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy the dependency file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose port 80 for the container
EXPOSE 80

# Use the entrypoint script as the container entrypoint
ENTRYPOINT ["./entrypoint.sh"]
