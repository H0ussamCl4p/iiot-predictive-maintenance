# ==========================================
# Simulator Dockerfile
# Runs the wear simulation script
# ==========================================

FROM python:3.10-slim

LABEL maintainer="IIoT Team"
LABEL description="Machine Wear Simulator"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY simulate_wear.py .

# Run the simulator
CMD ["python", "simulate_wear.py"]
