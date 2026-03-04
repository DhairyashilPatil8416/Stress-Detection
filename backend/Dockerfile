# Use Python 3.11 (compatible with mediapipe and tensorflow)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for OpenCV and Mediapipe
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements from backend/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole backend code
COPY . .

# Expose port (Render injects PORT automatically)
EXPOSE 8000

# Start FastAPI with Uvicorn
# If your entry file is main.py inside backend/, this works:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
