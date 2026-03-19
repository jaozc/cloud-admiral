# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY agent/     ./agent/
COPY collector/ ./collector/
COPY config/    ./config/
COPY main.py    .

# Non-root user for security
RUN useradd -m -u 1000 agentuser
USER agentuser

CMD ["python", "main.py"]
