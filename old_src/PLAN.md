# The Plan

A high level overview of the different code packages and files needed to create a fully functional League of Legends bot.

## Key Concepts

**Separation of concerns** - Each part of the program should focus on one specific task. No package or file should be responsible for too much at once.

**Code reuse** - Avoid writing repeat code. Use libraries or create your own "mini modules" to help with this.

**Encapsulation** - Files should build on each other; no single file should be too complicated, or contain too much code.

**Object-oriented** - Prefer object oriented programming over other programming paradigms.

**AI connectivity** - The more info the AI has, the higher skill / "human" cap it will have (in theory). Stuff like raw pixels of the screen to see pending ultimate usage or a log of chat during champ select would help with this.

## Packages

A description of the packages the program should use (no code files).
- **input**: Handles a bunch of different input sources, such as keyboard listening, screenshot collection, audio collection, etc.
  - keyboard: Listens for and responds to keyboard input from the user.
  - vision: Takes screenshots. Provides finding the location of buttons, reading text, etc.
  - hearing: Contains hearing tools.
- **output**: Handles a bunch of different output sources, such as mouse and keyboard emulators, opening and closing applications, etc.
  - logger: Logs info from the bot.
  - mouse: Emulates realistic mouse movements.
  - keyboard: Emulates realistic key presses and holds.
  - app_manager: Finds and manages applications.
- **game**: Contains the logic that plays the actual game.
  - control: Parses and interacts with on screen elements during the game.
  - logic: Decides what interactions to do during the game.
- **champ_select**: Contains the logic that runs champ select.
  - control: Parses and interacts with on screen elements during champ select.
  - logic: Decides what interactions to do during champ select.
- **menu**: Manages everything menu related, from parsing the screen to queueing up and starting the game. Also cleans up when the game is over. Does not handle champ select!
  - control: Parses and interacts with on screen elements in the menu.
  - logic: Decides what interactions to do in the menu.
- **client**: Combines the other packages (game, champ_select, and menu) to create a fully controllable League of Legends client.
  - control: Parses and interacts with the client.
  - logic: Decides what to do in the client.
- **gui**: Shows a friendly GUI to the user so they can control the league bot.
- **main**: Runs the program.

## Multiprocessing

Main process: GUI + QT event loop - Keyboard and mouse input handling

2nd process: Gathers input for the AI - Vision and hearing input handling

3rd process: Makes decisions using input from the first 2 processes - All logic handling