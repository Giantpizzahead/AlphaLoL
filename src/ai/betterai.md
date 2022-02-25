# Manual AI

What's a good strategy for the AI?

Minions, turrets, and players all share some characteristics:
* They have some amount of health
* They have a certain movement speed
* They do some amount of damage to specific targets depending on certain conditions

Turrets cannot move, have a big range, and deal a ton of damage.

Players have unpredictable stats, with potential changes depending on the spells they have available.

To play the game, the AI needs to know how "strong" their side is compared to the other in specific matchups. In ideal scenarios, the AI should consider the location of other champions on the map as well. This strength calculation influences whether the AI should play safe, neutral, or go all in.

The AI also needs to know how to play in each of these forms. For example, playing safe means staying well behind your minions, and only going up to last hit occasionally, not walking into turret range. Neutral means just that, including hitting turrets when allowed. All in means aiming for players only.

One way to decide what to do would be to have a way to calculate the "favorability" of a game state. This would return several things like how safe the AI is (risk), how likely the AI is to get a kill / take important objectives (reward), and how unpredictable each of these values are (range of possible actual risks and rewards). Then, try a bunch of possible strategies (could be macro or micro things), and simulate what the new game state might look like, calculating the new favorability of that. Take the best one, and execute that strategy.

Info needed for the AI:

* Minions: Allied, Type (melee, caster, cannon), Health, DPS
* In-lane objectives: Allied, Type (outer turret, inner turret, inhib, nexus turrets, nexus), Health, DPS, Range
* Players: Allied, Champion, Level, Health, Mana, Gold estimate, Abilities available, (Max possible) DPS
* GUI, excluding minimap: Precise health and mana, Ability cooldowns, CS, KDA, Game time
* Minimap: Turret locations, Allied/enemy champion locations, Champions, Camera location, Pings
* Other: Skillshots and ability animations, Movement prediction based on champion sprites, Jungle objectives
* Shop: Item names & costs, Gold

Info that's practical to collect manually:

* Minions: Allied, Health, Max health
  * Infer Type (melee, caster, cannon), DPS
* In-lane objectives: Allied, Health, Max health
  * Infer Type (outer turret, inner turret, inhib, nexus turrets, nexus), DPS, Range
* Players: Allied, Level, Health, Mana, Gold estimate
  * Estimate average DPS using Level and Mana
* GUI, excluding minimap: Precise health and mana, Ability cooldowns, CS, KDA, Game time
* Minimap: Camera location, Turret locations, Allied/enemy champion locations, Pings
* Shop: Item costs, Gold

AI should have a bunch of states:

* Base
  * Buy items and get back to laning
* Laning
  * Last hit, attack objectives, poke enemy
* Idling
  * Move around a bit while waiting for something
* Fighting
  * Look for the nearest, most favorable fight
  * Use all your abilities = ez pentakill
* Backing
  * Make sure you're safe, then recall
* Dead
  * RIP, wait for respawn
  * Spectate living allies
* End game
  * Victory or defeat?
  * Stop doing things when you see this
* Unknown
  * Fallback state
  * If this stays for too long, try to recall

In each state, the AI should do different things, and it should know when to switch states. Admittedly, this is a bit complicated for a starter AI though.

The main states that matter are Base, Laning, Idling, Fighting, and Backing. The other 3 are less important, and could be combined.

AI risk and reward calculation should consider:

* Health and DPS of nearby allies / enemies
  * Consider minions, turrets, and players
  * Track minion and turret aggro if possible
    * (Has attacked player recently)
  * Advanced: Remember location of things that recently went off-screen
* Location on minimap (in enemy territory?)
* Number of nearby allies on minimap
* Number of missing enemies on minimap

How to parse GUI?

Can locate Gold number at the start by comparing shop gold number with other numbers on screen

Run OCR on Tab, should be able to match champion portraits

## (Practical) Manual AI

Given:
* Location of the locked camera
* Location and % health of visible minions
* Location and % health of visible objectives
* Location, level, % health, and mana of visible champions

Create an AI that can perform well during the laning phase.

The bot will be an Annie one trick.

Set the right runes and create a custom item page using Mobalytics.

Abilities
* Order: qweqqrqwqwrwweeree
* Q: Point-and-click, 4 second cooldown
* W: Cone, 8 second cooldown
* E: Shield, 14/13/12/11/10 second cooldown
* R: Bear!, 120/100/80 second cooldown
* D: Flash, 300 second cooldown
* F: Ignite, 180 second cooldown

Keep track of stun passive stacks (somehow)

Stay passive in lane, using Q to last hit

When playing passive, position behind allied minions (or allied tower if no allied minions are nearby)

Look for low health enemy minions
Walk up, last hit either with Q (if up) or auto, then back off immediately
* If the enemy gets close, make sure to try and get some trade damage
* When trading, always use abilities while backing up

When stun is up, then you can be a bit more aggressive - Need to proc electrocute!

Look for low health ally minions
Position near them, if the enemy tries to last hit by walking up, trade with a combo

All-in if enemy health is below 70% at 3 or 4 stacks with E-W-Flash-R-Ignite-Q-AA.

Back off when the situation isn't favorable (too many enemies, too high level enemies, etc.)

Say glhf at the start of the game!