# AlphaLoL

100% original name

This is an applied machine learning project.

Version 0.2.1

## Demo

[Beginner Bot Game](https://www.youtube.com/watch?v=KWuxXuVBSl4&list=PLMhnlK6gpgE8hznQT_UEJ6PEKKHFgOIqW&index=5) (KDA: 5/0/3)

[Intro Bot Game](https://www.youtube.com/watch?v=1myX82e-rvc&list=PLMhnlK6gpgE8hznQT_UEJ6PEKKHFgOIqW&index=4) (KDA: 23/2/2)

Parsing the game state (minions, players, and turrets):

![Vision Demo 3](img/demo/vision_demo3.jpg)

![Vision Demo 5](img/demo/vision_demo5.jpg)

## Results

The bot can beat all tutorial parts consistently. It's also able to get an early lead and snowball it in Intro.

Versus Beginner bots, the bot does quite well in the early laning phase, and is able to identify some all in opportunities for kills. However, the bot tends to get confused when it sees other players, and it can end up doing some pretty dumb things, like standing still in a 2 versus 3 fight. Despite all this, it's able to maintain a solid KDA.

Current FPS of the bot ranges from 3 to 10 depending on available CPU/GPU power and how much stuff is on the screen.

## Usage

If you want to play around with the bot yourself, PLEASE be responsible. Stick to AI or Custom games. **Don't ruin the game for real players.** If you do go into an actual match, be ready to take over when the bot does something dumb.

To prevent usage as a leveling bot, **games cannot be started automatically.** You'll need to manually go through champ select, and activate the bot once the game starts.

While the bot is active, it'll give you a video window with the bot's interpretation of the game, along with a terminal window explaining the bot's logic (and other debug info).

## End User Setup

*Warning: Using a bot in an actual game is against the rules. You can get banned for it. Use at your own risk.*

These instructions only work for Windows.

1. Install Tesseract OCR and add it to your PATH. See this [installation guide](https://linuxhint.com/install-tesseract-windows/).
2. Download and run the AlphaLoL installer from the [latest release](https://github.com/Giantpizzahead/AlphaLoL/releases/latest).

When launching the bot, you might get some warnings related to Torch and Torchvision. You can safely ignore these.

To make the bot work, you'll need to configure some League game client options. Note: These settings assume that you're starting out with default options. If you've changed hotkeys related to core gameplay (not pings), you might need to change those back to default.

**Hotkeys**

1. Replace Quick Cast with Quick Cast with Indicator = Unchecked
2. Press the Quick Cast All button (to enable quick cast for all abilities).
3. Hotkeys > Player Movement > Player Attack Move Click = "A"

**Video**

1. Resolution = 1920x1080
2. (Optional) Window Mode = Windowed
3. (Optional) Graphics = Low
4. (Optional) Frame Rate Cap = 60 FPS

**Interface**

1. HUD Scale = 15
2. Cursor Scale = 50
3. Shop Scale = 44
4. Chat Scale = 100
5. Minimap Scale = 33
6. (Optional) Show Names Above Healthbar = Summoner Name

**Game**

1. Camera Lock Mode = Per-Side Offset
2. Attack move on cursor = Checked
3. Auto attack = Checked

When launching AlphaLoL, you'll see a menu displaying the hotkeys for the bot. In particular, press **Shift-T** to start and stop the bot.

## Todo: Modern AI

AI that uses a mix of manual logic and state-of-the-art deep learning to outperform the old Manual AI.

- [X] Begin to explore machine learning to create a better, more human-like AI
- [ ] Take some deep learning classes to figure out how we're going to approach this

### Milestones I: Back to Basics

  - [ ] Relearn the basics of the game.
  - [ ] Win an intro Coop vs AI game with a positive KDA & at least 3 kills
  - [ ] Learn how to execute an all-in.
  - [ ] Win a beginner Coop vs AI game with a positive KDA & at least 3 kills

### Milestones II: The Challenge

  - [ ] Learn how to dodge skillshots.
  - [ ] Win an intermediate Coop vs AI game with a positive KDA & at least 3 kills
  - [ ] Perform decently in a 1v1 vs an Iron player: Don't int in the first 3 minutes.
  - [ ] Get my account banned for using a bot (probably) (:/)
  - [ ] Learn how to use map awareness to avoid ganks.
  - [ ] Perform well in a 1v1 vs an Iron player: Get a solo kill in the first 10 minutes.

### Milestones III: The Extra Mile

  - [ ] Make a macro play in a real game that involves going out of lane - helping your jungler, objectives, or roams.
  - [ ] Win a Draft Pick game with >=0.5 KDA & at least 2 kills.
  - [ ] Master the art of skillshot dodging. Obtain "The Jukes!" challenge medal as proof.
  - [ ] Win a Draft Pick game with a positive KDA & at least 3 kills.

### Capstones: Good Luck

  - [ ] Win a Ranked Solo/Duo game with a positive KDA & at least 3 kills.
  - [ ] Get out of Iron IV.
  - [ ] Beat me in a 1v1 (first turret), but I play Soraka as a support - with support item and all.
  - [ ] Get out of Iron III.
  - [ ] Carry a Ranked Solo/Duo game with >=2 KDA & at least 10 kills.
  - [ ] Get out of Iron II.
  - [ ] Beat me in a 1v1 (first turret), but I play Morgana mid - skillshot dodging :o
  - [ ] Promote to Bronze IV!

## Todo: Manual AI (COMPLETE)

AI without machine learning - The "standard" way of doing it, with computer vision techniques (OpenCV) and hardcoded logic. I moved this list into `misc/TODO_MANUAL.md`.

## Development Setup

Warning: This repository is a bit of a mess. There are lots of old/unused files. Clone at your own risk :)

Use a virtual environment! See `requirements.txt` for a list of dependencies.
