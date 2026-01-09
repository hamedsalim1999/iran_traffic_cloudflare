FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create volume mount point for database
VOLUME ["/app/data"]

# Set environment variable for database path
ENV DB_PATH=/app/data/iran_traffic.db

# Run the application
CMD ["python", "-u", "main.py"]
