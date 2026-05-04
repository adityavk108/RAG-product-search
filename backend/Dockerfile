FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for faiss and other libs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first (much faster than CUDA version)
RUN pip install --no-cache-dir torch==2.1.2+cpu torchvision==0.16.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/images
RUN mkdir -p /app/cache/embeddings

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]