# AlphaLoL

*Warning: This bot has not been tested since the release of Vanguard, but since it makes no attempt to hide itself, it probably won't work anymore and will definitely be flagged.*

100% original name

This is an applied machine learning project.

Version 0.2.3

## Demo

[Beginner Bot Game](https://www.youtube.com/watch?v=KWuxXuVBSl4&list=PLMhnlK6gpgE8hznQT_UEJ6PEKKHFgOIqW&index=5) (KDA: 5/0/3)

[Intro Bot Game](https://www.youtube.com/watch?v=1myX82e-rvc&list=PLMhnlK6gpgE8hznQT_UEJ6PEKKHFgOIqW&index=4) (KDA: 23/2/2)

Parsing the game state (minions, players, and turrets):

![Vision Demo 3](img/demo/vision_demo3.jpg)

![Vision Demo 5](img/demo/vision_demo5.jpg)

## Results

The bot can beat all tutorial parts consistently. It's also able to get an early lead and snowball it in Intro.

Versus Beginner bots, the bot does quite well in the early laning phase, and is able to identify some all in opportunities for kills. However, the bot tends to get confused when it sees other players, and it can end up doing some pretty dumb things, like standing still in a 2 versus 3 fight. Despite all this, it's able to maintain a solid KDA.

Most importantly, there are 2 key issues keeping the bot from doing well in non-1v1 situations (and some beginner bots like Lux):

- Cannot see or dodge skillshots (they're too complicated and diverse to detect using manual vision)
- Does not have object persistence (if it can't see an object, it forgets about it)

These would likely need to be solved using deep learning techniques.

Current FPS of the bot ranges from 3 to 10 depending on available CPU/GPU power and how much stuff is on the screen.

## Usage

If you want to play around with the bot yourself, PLEASE be responsible. Stick to AI or Custom games. **Don't ruin the game for real players.** If you do go into an actual match, be ready to take over when the bot does something dumb.

To prevent usage as a leveling bot, **games cannot be started automatically.** You'll need to manually go through champ select, and activate the bot once the game starts.

While the bot is active, it'll give you a video window with the bot's interpretation of the game, along with a terminal window explaining the bot's logic (and other debug info).

## End User Setup

*Warning: Using a bot in an actual game is against the rules. You can get banned for it. Use at your own risk.*

Download and run the AlphaLoL installer from the [latest release](https://github.com/Giantpizzahead/AlphaLoL/releases/latest).

The bot only runs on Windows. Also, to make it work, you'll need to configure some League game client options. Note: These settings assume that you're starting out with default options. If you've changed hotkeys related to core gameplay (not pings), you *might* need to change those back to default.

**Hotkeys**

1. Replace Quick Cast with Quick Cast with Indicator = Unchecked
2. Press the Quick Cast All button (to enable quick cast for all abilities).
3. Hotkeys > Player Movement > Player Attack Move Click = "A"

**Video**

1. Resolution = 1920x1080 or 1680x1050 or 1280x1024, see below
2. (Optional) Window Mode = Windowed
3. (Optional) Graphics = Low
4. (Optional) Frame Rate Cap = 60 FPS

Note: If the bot runs slowly (<4 FPS when not shopping), lowering the resolution might help a lot. Make sure to keep a similar height though (in the 1000-1100 range), since that's used to navigate the shop GUI and calculate ability ranges.

The bot seems to perform optimally at 4-5.5 FPS, decently at 2.5-4 FPS, and poorly below *or* above that range.

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

Also, there are some gameplay specific things you'll want to set up:
- Enabled locked camera (press Y).
- Create a custom item page containing a good Annie build, see https://app.mobalytics.gg/lol/champions/annie/build. 
   There should only be one section. Name it "Optimal" (case-sensitive, the bot uses this to find the shop!).
   Put all items, including components, in order. The bot will simply right-click on each item in the given order
   whenever it can buy the next one. If done correctly, the bot should be able to just naively click one after the other
   and get a full build. (Remember to keep the 6 item inventory limit in mind!)
  - I use [this item set](https://pastebin.com/4ik52kCy), you can import it if you'd like.
  - Whatever you do, **do not use Banshee's Veil**. It changes the health bar color, which breaks the bot.
- Manually open and move the shop page so that the item set you made is selected and the items are bunched near the
   center of the screen. This isn't very strict, but you do need to place the *items* in the center (both horizontally
   and vertically), not the whole shop screen itself. See the screenshot below.
- Optional, but highly recommended for best results:
  - Use Flash on D and Heal on F for summoner spells.
  - Set and equip good rune page for Annie. Make sure to include Electrocute.

![Demo shop screen setup](https://i.gyazo.com/a09aa37af3330434cf06ab787b75522d.jpg)
*Example shop screen setup*

## Todo: Manual AI (COMPLETE)

AI without machine learning - The "standard" way of doing it, with computer vision techniques (OpenCV) and hardcoded logic.

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
- [X] Create a simple GUI to visualize the AI's actions
- [X] Cleanup the AI to make it perform better
- [ ] Fix a bug where the AI can't detect health bars of players shielded by Banshee's Veil
- [ ] Do some serious code cleanup and organizing so we don't hit a brick wall later on
- [X] Make the bot easier to setup on end user machines (ex: standalone installer, no Python venv required)

Nice-to-have but not as important things
- [ ] Add support for various resolutions
  - Do this by adding a relative scaled coordinate thing in window_tracker, and updating bounding boxes for vision (resolutions scale based on vertical size, horizontal only affects FOV)
- [ ] Try (and fail) to support Mac
- [X] Add error resiliency (handle infinite loops / exceptions gracefully)

### Milestones

  - [X] Perform a fixed coordinate combo (2/11/22)
  - [X] Perform a combo aimed at a champion (2/14/22)
  - [X] Beat Tutorial Part 1 with a positive KDA & at least 1 kill (2/14/22)
  - [X] Beat Tutorial Part 2 with a positive KDA & at least 1 kill (2/14/22)
  - [X] Beat Tutorial Part 3 with a positive KDA & at least 3 kills (2/15/22)

### Capstones

  - [X] Win an intro Coop vs AI game with a positive KDA & at least 3 kills (2/15/22, KDA: 23/2/2)
  - [X] Win a beginner Coop vs AI game with a positive KDA & at least 3 kills (2/24/22, KDA: 5/0/3)
  - [X] Win a 1v1 against me in a custom game (first turret), but I have to play Yuumi mid using a trackpad cause why not (2/24/22, KDA: 1/0/0)

## Development Setup

Warning: This repository is a bit of a mess. There are lots of old/unused files. Clone at your own risk :)

Use a virtual environment! See `requirements.txt` for a list of dependencies.
