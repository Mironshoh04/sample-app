FROM python:3.11-slim

# Set working directory
WORKDIR /home/myapp

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ./static ./static/
COPY ./templates ./templates/
COPY sample_app.py .

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /home/myapp
USER appuser

# Expose port
EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5050/api/health || exit 1

# Run application
CMD ["python", "sample_app.py"]
