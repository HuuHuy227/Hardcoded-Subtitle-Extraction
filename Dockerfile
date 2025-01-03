FROM nvidia/cuda:12.0.1-cudnn8-devel-ubuntu22.04

WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y wget python3-dev gcc && \
    apt-get install -y --no-install-recommends libopencv-dev && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py
    
RUN apt-get update && apt-get install -y build-essential \
    cmake \
    wget \
    git \
    unzip \
    yasm \
    pkg-config \
    libjpeg-dev \
    libtiff-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran \
    libtbb2 \
    libtbb-dev \
    libpq-dev \
    && apt-get -y clean all \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app	
RUN pip install paddlepaddle-gpu==2.6.1.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app /app


