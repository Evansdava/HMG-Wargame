# Welcome to HexMapGen

This is a hex-based map generator for making small-scale battlemaps as would be used in Lancer, Dungeons and Dragons, or other tabletop RPGs.

## Using this Program:

It is currently [live on Heroku](https://hexmapgen.herokuapp.com) (it may take a minute for the dynos to spin up), or you can download or clone the files (`git clone`).
Once downloaded, set up a virtual environment (`python3 -m venv env`) and install the requirements (`pip3 install requirements.txt`).
From there, you can host the server locally with the command `flask run`.

The home page (which also has instructions and descriptions) provides several options to adjust how the map is generated. The impacts of these are described later, in the [How it Works](#how-it-works) section. These options can be left as default or changed to suit your liking.

Once you've set some options, click "Generate" and a map will be made using those options.
From the Map screen, you can decide to generate another map with the same settings. If you do so, the map will be lost.
To avoid this, you can save the map. If you wish, you can also change the name of the map before (or after) saving.
Once saved, you can always come back to the map screen with the url "https://hexmapgen.herokuapp.com/map/{Map-Name}"
You can delete a map you've saved from the map screen.

On any screen, you can use the Navbar to reach another screen. Clicking the name of the site, or "Home" will take you to the home page, with the options to generate a new map. "Map" will take you directly to a newly generated map using the default options. "Saved Maps" takes you to the list of all currently saved maps.

## How it Works:

### Each hex on the map is an object of the Hex class. The hex object has several properties:

* An id number: keeping track of its position in the map
* References to the next adjacent hex on every side
* The contents of the hex (terrain)


### The map is itself an object of the Map class that contains all associated hex objects, as well as a few other properties:

* Name (The name of the map)
* Length (The number of rows in the map)
* Width (The number of hexes in a particular row)
* Percentage chances for each type of terrain to appear in any given hex.

Chances are represented as floating point (decimal) numbers with a value from 0 to 1.
Though it's possible to input a value higher than 1, it may cause erroneous behavior.

### The different types of terrain have different chances to appear:

1. Forests are represented in green, and can spawn anywhere, and are more likely to spawn next to other forests. By default, they have a 10% chance to appear on a given hex, or 20% next to other forests.
1. Rivers are represented in blue, spawn from an edge, and meander across the map afterwards. Rivers can overwrite forests that are in their path. By default, they have a 2% chance to appear on any given edge tile
1. Roads are represented in orange, spawn from an edge, and follow straight lines to another edge. Roads can overwrite rivers and forests in their path. By default, they also have a 2% chance to appear on any given edge tile.
1. Buildings are represented in red, spawn next to roads or other buildings, and can overwrite forests, but not rivers or roads. By default, they have a 20% chance to spawn on a square adjacent to a road or other building.
1. Anywhere without other terrain is gray

## Known Issues:

* Maps larger than 30 hexes wide will be displayed incorrectly, though this can be fixed by zooming the browser out
* Occasionally on the Heroku deployment, saving a map will not work correctly, instead generating a new map with the same name

## Technologies used:

This project was written in Python 3 on a Flask development server, with Jinja2 templating to display maps and Bootstrap 4 for formatting.

Redis is used for the database to store and retrieve maps.

Names are generated randomly by the Uzby API.
