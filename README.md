# Video Hardcoded Subtitle Extractor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Extract hardcoded/burned-in subtitles from videos using OCR technology. Available as both a desktop application and web interface.

## 🎯 Features

- GUI and web interface options
- Support for MP4, AVI, MOV video formats
- Adjustable frame rate and confidence threshold
- Multiple language support
- Real-time progress tracking
- SRT export format
- GPU acceleration support

## ⚙️ Requirements

- Python 3.8+
- NVIDIA GPU (optional)
- CUDA Toolkit 12.0+ (for GPU acceleration)
- 4GB RAM minimum (8GB recommended)

## 📥 Installation

### Option 1: Python Package

```bash
# Clone repository
git clone https://github.com/yourusername/subtitle-extractor.git
cd subtitle-extractor

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# For GPU support (optional)
pip install paddlepaddle-gpu==2.6.1

### Option 2: Conda Environment

```bash
# Create conda environment
conda create -n subtitle-env python=3.8
conda activate subtitle-env

# Install dependencies
pip install -r requirements.txt

# For GPU support (optional)
conda install paddlepaddle-gpu==2.6.1

### Option 3: Docker
### CPU Version

```bash
# Build and run
docker-compose build
docker-compose up

### GPU Version
```bash
# Install NVIDIA Container Toolkit first
# Then build and run with GPU support
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up

### 🚀 Usage
### Desktop Application
```bash
# Launch GUI
python gui.py

### Web Interface
```bash
# Launch web app
streamlit run app.py

## ⚙️ Configuration
### Docker Volume Mounting
Mount your video directory in docker-compose.yml:
```bash
volumes:
  - C:/your/video/path:/app/videos

Environment Variables
```bash
VIDEO_INPUT_DIR=/path/to/videos  # Default video directory

### 🤝 Contributing
- Fork the repository
- Create a feature branch
- Commit changes
- Push to branch
- Create pull request