FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs state generated_projects

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.health import HealthChecker; from app.config import AgentConfig; from pathlib import Path; c = AgentConfig(); h = HealthChecker(c.memory_db_path, c.workspace_root); s = h.check(); exit(0 if s.status != 'unhealthy' else 1)"

# Run the application
CMD ["python", "main.py"]
