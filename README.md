# Welcome to HexMapGen Wargame

This is a Risk-style simulation using the [Hexagon Based Map Generator](https://hexmapgen.herokuapp.com) I built as a basis.

## Using this Program:

It is currently [live on Heroku](https://hmg-wargame.herokuapp.com) (it may take a minute for the dynos to spin up), or you can download or clone the files (`git clone`).
Once downloaded, set up a virtual environment (`python3 -m venv env`) and install the requirements (`pip3 install requirements.txt`).
From there, you can host the server locally with the command `flask run`. Or, you can run the simulation in the terminal from the `game.py` file.
Simply run the command `python3 game.py`

The home page (which also has instructions and descriptions) provides several options to adjust how the map is generated. These options can be left as default or changed to suit your liking. The only new option introduced in Wargame is the number of kingdoms to start

Once you've set some options, click "Generate" and a map will be made using those options.
After a map has been generated, clicke "Run Simulation" to begin the simulation. You can stop it with the "Stop Simulation" button.
While the game is running, you can open the browser console (via Right Click > Inspect Element) to view stats of each kingdom.

From the Map screen, you can decide to generate another map with the same settings. If you do so, the map will be lost.
To avoid this, you can save the map. If you wish, you can also change the name of the map before (or after) saving.
Once saved, you can always come back to the map screen with the url "https://hmg-wargame.herokuapp.com/map/{Map-Name}"
You can delete a map you've saved from the map screen.

On any screen, you can use the Navbar to reach another screen. Clicking the name of the site, or "Home" will take you to the home page, with the options to generate a new map. "Map" will take you directly to a newly generated map using the default options. "Saved Maps" takes you to the list of all currently saved maps.

## How it Works:

See the [README for HexMapGen](https://github.com/Evansdava/HexMapGen) for details on map generation.

### Rules for the Wargame

#### Each kingdom has three types of power:
* Military
* Administrative
* Diplomatic


Military power, in abstract, represents the amount and quality of troops, weapons, machines, and other tools of war available. It is used for attacks, and increases with a kingdom's size and with the buildings conquered. It decreases when losing territory.

Administrative power represents how effectively a kingdom can function, including raising taxes, passing and enforcing laws, creating and supplying armies, and so on. The more a kingdom expands, the more adminstrative power it needs. It increases somewhat with size, by conquering roads, and by taking the stabilize action. It decreases when losing territory.

Diplomatic power represents the efficacy of a kingdom's diplomats, spies, courtiers, and other agents of foreign affairs. Diplomatic power makes it easier to forge alliances and makes it more difficult for others to break them. It increases with forests and rivers controlled, and by maintaining alliances. It is reduced when breaking alliances.


Conflicts are the method of interacting with other kingdoms. A conflict can be of any power. Conflicts are resolved when each kingdom rolls a die of a number of sides equal to the total size of the map. If this roll is under the corresponding power number, that roll is successful. If both kindoms in a conflict are successful or unsuccessful, the roll is repeated until one is successful and the other is not.



### On its turn, a kingdom can perform one of three actions:

* Attack
* Ally
* Stabilize


Attacking is the way to grow one's borders. A kingdom can attack a number of times equal to the number of border tiles you have. If the attack targets an unoccupied tile, that tile is automatically taken. Against another kingdom, attacking triggers a military conflict, the winner of which gains or retains control of the tile.

##### Conditions to attack:
* Territory is adjacent
* Admin is high enough

##### Modifiers to attack:
\+ Tile is unowned
\+ Tile terrain is desirable
\+ Owner of tile is weaker
\+ Owner of tile is a rival
\+ Owner of tile is a rival of an ally
\+ Tile is adjacent to multiple controlled tiles
\- Owner of tile is stronger
\- Owner of tile is an ally


Allying is a way for a kingdom to protect itself against threats. Kingdoms are less likely to attack an ally's tiles, and must win a diplomatic conflict to do so at all. Kingdoms are more likely to attack the tiles of an ally's rival. Each kingdom has one rival, which is usually the largest threat to the kingdom. When allying a target, a diplomatic conflict is triggered, and if successful, an alliance is formed.

##### Conditions to ally:
* Target is not a rival
* The target's rival is not the kingdom

##### Modifiers to ally:
\+ Target and kingdom have the same rival
\+ Target is stronger
\+ Other kingdoms pose a large threat
\- Target poses a large threat
\- Target has adjacent tiles
\- Target is weaker


Stabilizing is how kingdoms gain more Administrative power. It also temporarily raises Military power. When stabilizing, an administrative conflict is triggered against a kingdom's rival. If the rival kingdom wins, the increases to both Administrative and Military power are halved.

##### Conditions to stabilize:
* None

##### Modifiers to stabilize:
\+ More Administrative power is required to conquer territory
\+ All neighboring kingdoms are stronger
\- There are easy targets for expansion
\- More Administrative power is not required

## Known Issues:

* Maps larger than 30 hexes wide will be displayed incorrectly, though this can be fixed by zooming the browser out
* Occasionally on the Heroku deployment, saving a map will not work correctly, instead generating a new map with the same name

## Technologies used:

This project was written in Python 3 on a Flask development server, with Jinja2 templating to display maps and Bootstrap 4 for formatting.

Redis is used for the database to store and retrieve maps.

Names are generated randomly by the Uzby API.

Browser scripting is written in Python using Brython
