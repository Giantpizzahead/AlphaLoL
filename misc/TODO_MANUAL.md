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
