# Video Hardcoded Subtitle Extractor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
Extract hardcoded/burned-in subtitles from videos using OCR technology. Available as both a desktop application and web interface.

## 🎯 Features
- GUI and web interface options
- Support for MP4, AVI, MOV video formats
- Adjustable frame rate and confidence threshold
- Multiple language support (English, Chinese, Japanese, Korean, Arabic)
- SRT export format. Also supported bilingual subtitles.
- **Note:** For long video process recommend install GPU version for efficient of speed process (about 1/5 the length of the video)


## ⚙️ Requirements
- Python 3.8+
- NVIDIA GPU (optional)
- CUDA Toolkit 11.8, 12.0+ (for GPU acceleration)
- 4GB RAM minimum (8GB recommended)

## 📥 Installation

### Option 1: Conda Environment 

```bash
# Create conda environment
conda create -n subtitle-env python=3.10
conda activate subtitle-env
# For GPU support (optional)
pip install paddlepaddle # pip install paddlepaddle-gpu==2.6.1 for GPU version
# Install dependencies
pip install -r requirements.txt
```

### Option 2: Docker
```bash
# Install NVIDIA Container Toolkit first
# Then build and run with GPU support
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
```

### 🚀 Usage
### Desktop Application
```bash
# Launch GUI
python gui.py
```
![Alt Text](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ0ejlkbXY2OGxkOXY0azlwZ2ttOHMxbnB4eDVsdDRlbTBmbmk0bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Mk4QxIiNl1V2lx9afi/giphy.gif)
### Web Interface
```bash
# Launch web app
streamlit run app.py
```
![Alt Text](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTk2NWpnbXI5MWV6ZzVoYmIwODZpdzNtZnVybHF1N2JrempybjY1dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3Y1bedk8LoZkPi18OK/giphy.gif)

[Link Demo](https://www.youtube.com/watch?v=2ZxI7lb3C2I)
### 🤝 Credits
- PaddleOCR
