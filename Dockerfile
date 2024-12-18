FROM paddlepaddle/paddle:3.0.0b2-gpu-cuda11.8-cudnn8.6-trt8.5

WORKDIR /app	
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app /app


