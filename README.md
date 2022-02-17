# AlphaLoL

100% original name

Bot that tries to play League of Legends automatically.

This is an applied machine learning project.

Version 0.1.1

## Demo

[Intro Bot Game](https://www.youtube.com/watch?v=1myX82e-rvc&list=PLMhnlK6gpgE8hznQT_UEJ6PEKKHFgOIqW&index=4) (KDA: 23/2/2) 

Parsing the game state (minions, players, and turrets):

![Vision Demo 3](img/demo/vision_demo3.jpg)

![Vision Demo 5](img/demo/vision_demo5.jpg)

Playing the game using the parsed info:

![Manual AI Demo 1](img/demo/manual_ai_demo1.jpg)

## Results

The bot can beat all tutorial parts consistently. It's also able to get an early lead and snowball it in Intro.

However, it's not able to do this versus Beginner bots. Sometimes humans confuse the bot (guide it towards jungle monsters, go in under turret). Sometimes the bot is just dumb (executed by tower, run into the center of 4 enemies).

Current FPS of the bot hovers from 4 to 5 depending on how much stuff is on the screen.

## Usage

If you want to play around with the bot yourself, PLEASE be responsible. Stick to AI or Custom games. **Don't ruin the game for real players.**

If you do go into an actual match, be ready to take over when the bot does something dumb. Don't let the bot feed.

To prevent usage as a leveling bot, games cannot be started automatically. You'll need to manually go through champion select, and activate the bot once the game starts.

## Setup

Um... yeah. Good luck with that one.

Use a virtual environment with Python 3.9. Python 3.10 will not work! Other versions have not been tested.

Windows setup:
Clone the respoitory, activate your virtual environment, navigate to the `src` directory, and run the below commands.
```shell
# All systems
pip install colorlog
pip install pynput
pip install numpy
pip install matplotlib
pip install mss
pip install editdistance

# Windows specific
pip install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio===0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
pip install pywin32

# All systems
pip install easyocr
pip uninstall opencv-python-headless
pip install opencv-python==4.5.4.60

# Start the bot
python main.py
```

## Todo

- [X] Create basic controllers
  - [X] Basic mouse movements, semi-realistic
  - [X] Basic keyboard controls
  - [X] Basic League-specific "combos" (ex: aim then press an ability)
- [X] Use vision to locate objects on the screen
  - [X] Locate champions within the camera's view, and identify their loyalty / health
  - [X] Locate turrets within the camera's view, and identify their loyalty / health
  - [X] Locate minions within the camera's view, and identify their loyalty / health
- [X] Create an AI with simple, hardcoded logic by combining vision and controllers
- [X] Optimize image processing so the frame rate is at least manageable
- [X] Use vision to help the AI buy recommended items from the shop
- [ ] Create a simple GUI to visualize the AI's actions
- [ ] Cleanup the AI to make it perform better
- [ ] Do some serious code cleanup and organizing so we don't hit a brick wall later on

Nice-to-have but not as important things
- [ ] Add support for various resolutions
  - Do this by adding a relative scaled coordinate thing in window_tracker, and updating bounding boxes for vision (resolutions scale based on vertical size, horizontal only affects FOV)
- [ ] Try (and fail) to support Mac
- [ ] Add error resiliency (handle infinite loops / exceptions gracefully)

### Milestones: Manual AI

  - [X] Perform a fixed coordinate combo (2/11/22)
  - [X] Perform a combo aimed at a champion (2/14/22)
  - [X] Beat Tutorial Part 1 with a positive KDA & at least 1 kill (2/14/22)
  - [X] Beat Tutorial Part 2 with a positive KDA & at least 1 kill (2/14/22)
  - [X] Beat Tutorial Part 3 with a positive KDA & at least 3 kills (2/15/22)

### Capstones: Manual AI

  - [X] Win an intro Coop vs AI game with a positive KDA & at least 3 kills (2/15/22, KDA: 23/2/2)
  - [ ] Win a beginner Coop vs AI game with a positive KDA & at least 3 kills
  - [ ] Win a 1v1 against me in a custom game (first turret), but I have to play Yuumi mid cause why not

### Milestones: Hybrid AI

TBD
