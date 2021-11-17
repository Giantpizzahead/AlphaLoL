# lol-bot

LoL bot. Will boost you to Iron IV

This bot makes no effort to stay undetected, because it doesn't even work. Use at your own risk.

Dedicated to all chat (rip)

## Setup

### All operating systems

1. Clone the repository
2. Make a Python 3 virtual environment (recommended)
3. Install package dependencies
4. Make sure League is installed and you're signed in to an **throwaway** account (it will probably get banned!).
5. Run main.py

Package dependencies:
```shell
pip install pynput
pip install colorlog
pip install numpy
pip install opencv-python
pip install mss
```

### Windows
1. Additional packages:
```shell
pip install pywin32
```

### Mac
1. Additional packages:
```shell
pip install pyobjc
```
2. Allow access to Accessibility, Input Monitoring, and Screen Recording

## Todo

### Tasks

- [X] Open the client automatically
  - [X] Mac
  - [ ] Windows
  - [ ] Linux
- [ ] Code style
  - [X] Separated folders
  - [ ] Threads for GUI, user input listener, and AI
  - [ ] Avoid hardcoding when possible
- [X] Understand the current state of the client
  - [X] Able to recognize current screen
  - [X] Able to navigate client from home screen
  - [X] Able to close pop-up boxes
- [ ] Start games automatically
  - [X] Tutorial, all parts
  - [ ] Coop vs. AI, all difficulties
  - [ ] Blind Pick
  - [ ] Draft Pick
  - [ ] Ranked
- [ ] Understand and participate in champ select
  - [ ] Choose champion
  - [ ] Ban champion(s)
  - [ ] Choose summoners
  - [ ] Choose runes
  - [ ] Type in chat
  - [ ] Consider already chosen champions
  - [ ] Dodge if win chance is low
- [ ] Understand the current state of the game
  - [ ] Minions
  - [ ] Champions
  - [ ] Towers / Nexus
  - [ ] Health / Mana
  - [ ] Gold
  - [ ] Objectives
  - [ ] Jungle camps
- [ ] Play a few champs well (beat beginner bots) with hardcoded logic
  - [ ] Yummi supp
  - [ ] Miss Fortune bot
  - [ ] Lux mid
  - [ ] Sett top
  - [ ] Master Yi jungle
  - [ ] Bonus: Heimerdinger mid
  - [ ] Bonus: Nocturne jungle
- [ ] Automatically learn how to play the game
  - [ ] Machine learning

### Milestones

Beat means getting consistently positive KDA (kills + assists/2 > deaths).

- [ ] Beat Tutorial Part 1
  - [ ] Move / Attack move
  - [ ] Auto attack
- [ ] Beat Tutorial Part 2
  - [ ] Use abilities
  - [ ] Choose targets to aim at
- [ ] Beat Tutorial Part 3
  - [ ] Buy recommended items
  - [ ] Recall at low health
- [ ] Beat Intro Bots
- [ ] Beat Beginner Bots
  - [ ] Use emotes
  - [ ] Type in chat
- [ ] Beat Intermediate Bots
- [ ] Win a Blind Pick game
- [ ] Win a Draft Pick game

Made by <a href="https://github.com/Giantpizzahead">Giantpizzahead</a>