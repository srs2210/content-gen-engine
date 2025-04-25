# Step 1: Use an official NVIDIA CUDA runtime image based on Ubuntu 20.04.
# This image includes CUDA 12.1 runtime libraries and uses Ubuntu 20.04 (focal) as its base.
# Ubuntu 20.04 typically comes with Python 3.8 by default.
FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04

# Set environment variables to ensure Python 3 uses UTF-8
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Step 2: Install Python 3 (python3 on Ubuntu 20.04 is ~3.8), pip, and essential build tools.
# python3-dev is needed for compiling some Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip using python3
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Step 3: Copy requirements.txt first (for Docker layer caching)
COPY requirements.txt /app/

# Step 4: Install PyTorch, TorchVision, and Torchaudio compatible with CUDA 12.1.
# These specific versions will satisfy your ">=1.7.1" for torch and ">=0.8.2" for torchvision.
# These wheels are compatible with Python 3.8.
# Remember to remove torch, torchvision, and torchaudio from your requirements.txt file.
RUN python3 -m pip install --no-cache-dir \
    torch==2.3.0+cu121 \
    torchvision==0.18.0+cu121 \
    torchaudio==2.3.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Step 5: Install other dependencies from requirements.txt
# These dependencies must be compatible with Python 3.8.
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the rest of your application code
COPY . /app

# Step 7: Expose the port your application runs on
EXPOSE 3001

# Step 8: Define the command to run your application
# This will use the default python3 (likely 3.8) in the container.
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001", "--workers", "4"]
