1. Create a virtual environment
2. Install dependencies
```shell
# All systems
pip install colorlog
pip install pynput
pip install numpy
pip install matplotlib
pip install mss
pip install editdistance

# Windows specific
pip install torch torchvision torchaudio
pip install pywin32

# All systems
pip install easyocr
pip uninstall opencv-python-headless
pip install opencv-python

# Start the bot
python main.py
```