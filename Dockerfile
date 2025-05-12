# Use official Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and Redis
RUN apt-get update && apt-get install -y \
    g++ \
    netcat-openbsd \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copy application files
COPY image_processing.proto .
COPY image_input_service.py .
COPY face_landmark_detection_service.py .
COPY age_gender_estimation_service.py .
COPY data_storage_service.py .
COPY config.json .

# Generate gRPC code
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_processing.proto

# Command will be specified in docker-compose.yml
CMD ["python", "image_input_service.py"]