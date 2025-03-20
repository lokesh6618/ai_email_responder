FROM python:3.9-slim

# Set environment variables to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    libatlas-base-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Set the working directory
WORKDIR /app

COPY requirements.txt .

# Upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python"]
