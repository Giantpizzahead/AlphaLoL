# lol-bot

LoL bot. Will boost you to Iron IV

This bot makes no attempt to stay undetected, because it doesn't even work. Use at your own risk.

Version 0.0.0

## Setup

Um... yeah. Good luck with that one.

Use a virtual environment with Python 3.9 or below. Python 3.10 will not work!

Dependencies:
```shell
pip install colorlog
pip install pynput
pip install numpy
pip install matplotlib
pip install mss

# Windows specific
pip install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio===0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

# Mac specific (DOES NOT WORK RIGHT NOW)
pip install torchaudio
pip install --upgrade torch==1.9.0
pip install --upgrade torchvision==0.10.0

# All systems
pip install easyocr
pip uninstall opencv-python-headless
pip install opencv-python==4.5.4.60
```

## Todo

- [X] Create basic controllers
  - [X] Basic mouse movements, semi-realistic
  - [X] Basic keyboard controls
  - [X] Basic League-specific "combos" (ex: aim then press an ability)
- [ ] Use vision to locate objects on the screen
  - [X] Locate champions within the camera's view, and identify their loyalty / health
  - [ ] Locate turrets within the camera's view, and identify their loyalty / health
  - [X] Locate minions within the camera's view, and identify their loyalty / health
- [ ] Create an AI with simple, hardcoded logic by combining vision and controllers

### Milestones: Manual AI

  - [X] Perform a fixed coordinate combo (2/11/22)
  - [ ] Perform a combo aimed at a champion
  - [ ] Beat Tutorial Part 1 with a positive KDA & at least 1 kill
  - [ ] Beat Tutorial Part 2 with a positive KDA & at least 1 kill
  - [ ] Beat Tutorial Part 3 with a positive KDA & at least 3 kills
