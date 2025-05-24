#!/bin/bash

echo "🚀 Building Enhanced Sample App with API capabilities..."

# Clean up any existing containers and temp directories
echo "🧹 Cleaning up existing containers..."
docker stop samplerunning 2>/dev/null || true
docker rm samplerunning 2>/dev/null || true
rm -rf tempdir

# Create temporary directory for Docker build
echo "📁 Creating build directory..."
mkdir tempdir
mkdir tempdir/templates
mkdir tempdir/static

# Copy application files
echo "📋 Copying application files..."
cp sample_app.py tempdir/.
cp requirements.txt tempdir/.
cp -r templates/* tempdir/templates/.
cp -r static/* tempdir/static/.

# Create optimized Dockerfile
echo "🐳 Creating Dockerfile..."
cat > tempdir/Dockerfile << 'EOF'
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
EOF

# Build Docker image
echo "🔨 Building Docker image..."
cd tempdir
docker build -t enhanced-sampleapp:latest .

# Run Docker container with enhanced configuration
echo "🌐 Starting container..."
docker run -t -d \
    -p 5050:5050 \
    --name samplerunning \
    --restart unless-stopped \
    --health-cmd="curl -f http://localhost:5050/api/health || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    enhanced-sampleapp:latest

# Wait for container to be ready
echo "⏳ Waiting for application to start..."
sleep 5

# Display container status
echo "📊 Container status:"
docker ps -a | grep samplerunning

# Test the application
echo "🧪 Testing application endpoints..."
echo "Health check:"
curl -s http://localhost:5050/api/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"

echo ""
echo "✅ Enhanced Sample App deployment complete!"
echo "🌐 Access the application at: http://localhost:5050"
echo "📚 API Documentation available at: http://localhost:5050/api/"
echo "🔍 Available endpoints:"
echo "   - GET / (Main dashboard)"
echo "   - GET /api/health (Health check)"
echo "   - GET /api/weather/<city> (Weather data)"
echo "   - GET /api/quote (Random quote)"
echo "   - GET /api/user (Random user)"
echo "   - GET /api/crypto/<symbol> (Crypto price)"
echo "   - GET /api/system-info (System information)"