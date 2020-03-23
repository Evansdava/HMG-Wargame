try:
    from static.scripts.python.hex import Hex
    from static.scripts.python.kingdom import Kingdom
except ModuleNotFoundError:
    from hex import Hex
    from kingdom import Kingdom
from random import random, choice


class Map(object):
    """The class for an overall map made of hexes"""

    def __init__(self, name="", length=15, width=15,
                 for_chance=0.2, riv_chance=0.04,
                 road_chance=0.04, build_chance=0.3,
                 kingdoms=0):
        """Initialize values from which to generate terrain"""
        self.name = name

        # Dimensions, number of rows and columns for length/width respectively
        self.length = int(length)
        self.width = int(width)

        # Keeping track of associated hexes, both specific and a count
        self.hexes = []
        self.len = 0

        # Chances for each type of terrain to be generated, as a float 0-1
        self.for_chance = float(for_chance)
        self.riv_chance = float(riv_chance)
        self.road_chance = float(road_chance)
        self.build_chance = float(build_chance)

        # Generating the map
        self.generate()

        # Populating the map with kingdoms
        self.kingdoms = []
        for king in range(int(kingdoms)):
            tile = choice(self.hexes)
            while tile.owner is not None:
                tile = choice(self.hexes)
            self.kingdoms.append(Kingdom(str(king), self, [tile]))

    def __str__(self):
        """Return a string visualization of the map"""
        string = ""
        count = 0
        for hex in self.hexes:
            # Checking for the start of rows
            if hex.ML is None:
                # Every other row, indent the hexes
                if count % 2 == 0:
                    string += f"{hex}"
                else:
                    string += f"  {hex}"
            # Checking that the row hasn't ended
            if hex.MR is not None:
                string += f" {hex.MR}"
            else:
                string += '\n'
                count += 1
        return string

    def __getitem__(self, position):
        return self.hexes[position]

    def edge_crawl(self, key, chance):
        """Travels around edges and starts features based on a random chance.

        Arguments:
            key - string that represents terrain to be placed
            chance - float from 0-1 for checking if features are made on a hex

        Returns: list of hexes which were changed
        """
        # Starts at the first hex
        current_hex = self.hexes[0]
        starts = []
        # Travels along the top until hitting the end of a row
        while current_hex.MR is not None:
            if random() < chance:
                current_hex.terrain = key
                starts.append(current_hex)
            current_hex = current_hex.MR

        # Travels down along the right until hitting the bottom
        while current_hex.BL is not None:
            if random() < chance:
                current_hex.terrain = key
                starts.append(current_hex)
            if current_hex.BR is None:
                current_hex = current_hex.BL
            else:
                current_hex = current_hex.BR

        # Travels along the bottom until hitting the start of a row
        while current_hex.ML is not None:
            if random() < chance:
                current_hex.terrain = key
                starts.append(current_hex)
            current_hex = current_hex.ML

        # Travels along the left until hitting the top
        while current_hex.TR is not None:
            if random() < chance:
                current_hex.terrain = key
                starts.append(current_hex)
            if current_hex.TL is None:
                current_hex = current_hex.TR
            else:
                current_hex = current_hex.TL

        return starts

    def check_edge(self, tile):
        """Checks which edge a tile has and returns the opposite direction.

        Argument:
            tile - hex which is being checked

        Returns: string representing the direction away from an edge
        """
        current_hex = tile
        # Checks the sides first, to eliminate ambiguity over TL/BL
        if current_hex.ML is None:
            direction = "r"
        elif current_hex.MR is None:
            direction = "l"
        elif current_hex.BL is None:
            direction = "u"
        elif current_hex.TL is None:
            direction = "d"
        return direction

    def generate(self):
        """Main function to create map"""
        # First creates a grid of hexes without terrain
        for row in range(self.length):
            # Every other row has one fewer hex
            if row % 2 == 0:
                width = self.width
            else:
                width = self.width - 1

            for col in range(width):
                new_hex = Hex(self.len, ".")
                # Keep track of hexes that have been made
                self.hexes.append(new_hex)
                self.len += 1

                # Determining the necessary connections for each new hex
                # Connections other than Mid-Left, Top-Left, and Top-Right are
                # redundant.
                # Tuples are formatted (SIDE, NUM) where NUM is the number of
                # hexes to count backwards to be accurate

                # Check if it's on the top row
                if row == 0:
                    # The top left corner initiates no connections
                    if col == 0:
                        tup = (("", 0),)
                    # The others only have one
                    else:
                        tup = (("ML", 2),)
                else:
                    # The leftmost hex in each column connects to one or two
                    if col == 0:
                        if row % 2 == 0:
                            tup = (("TR", self.width),)
                        else:
                            tup = (("TL", self.width + 1), ("TR", self.width))
                    # The last hex in every other row doesn't have a TR
                    # connection
                    elif col == width - 1 and row % 2 == 0:
                        tup = (("ML", 2), ("TL", self.width + 1))
                    else:
                        tup = (("ML", 2),
                               ("TL", self.width + 1),
                               ("TR", self.width))

                # Loop through each side needed and make connections
                for side, num in tup:
                    try:
                        new_hex.connect(side, self.hexes[self.len - num])

                    # In case I missed any edge cases, skipping over them
                    except IndexError:
                        pass

        # Generate each feature in order of precedence
        self.generate_forests()
        self.generate_rivers()
        roads = self.generate_roads()
        self.generate_buildings(roads)

    def generate_forests(self):
        """Checks if random tiles or their neighbors are forests"""
        forests = []
        # A number of checks based on how many hexes are present
        for _ in range(int(self.len / 10)):
            # print(self)  # To visualize generation in real time
            current_hex = choice(self.hexes)
            if random() < self.for_chance:
                current_hex.terrain = "F"
                forests.append(current_hex)

        # The array expands as more tiles are turned, possibly making far more
        for tile in forests:
            for neighbor in tile.check_neighbors():
                # print(self)  # To visualize generation in real time
                # A higher chance to spawn next to another forest than on its
                # own, to encourage clustering
                if random() < self.for_chance * 2:
                    neighbor.terrain = "F"
                    forests.append(neighbor)
        # return forests

    def generate_rivers(self):
        """First checks if a river starts in an edge hex, then extends any"""
        # Start by generating starts along the edges
        river_starts = self.edge_crawl("W", self.riv_chance)
        rivers = river_starts.copy()

        for river in river_starts:
            # Begins travelling away from the edge
            direction = self.check_edge(river)
            current_hex = river

            # Travels until it reaches an edge
            while current_hex is not None:
                # print(self)  # To visualize generation in real time
                current_hex.terrain = "W"
                rivers.append(current_hex)
                # Chooses a random direction that tends towards the same path
                current_hex = choice(current_hex.get_direction(direction))[0]
        return rivers

    def generate_roads(self):
        """Chooses an edge tile and extends in a random direction"""
        # Begin by generating starts along the edges
        road_starts = self.edge_crawl("R", self.road_chance)
        roads = road_starts.copy()

        for road in road_starts:
            direction = self.check_edge(road)
            # If on the top or bottom, the road may alternate sides to follow
            if direction == "u":
                options = ("TL", "TR")
            elif direction == "d":
                options = ("BL", "BR")
            # If not, then the variable doesn't matter
            else:
                options = None
            # Bool to track if the road goes straight up (alternating sides)
            straight = False
            # Chooses a random direction to follow away from the edge
            path = choice(road.get_direction(direction))[1]
            current_hex = road

            # If the road is on the top or bottom, it has a 50/50 to go
            # straight up/down or pick one direction
            if options is not None:
                if random() < 0.50:
                    path = choice(options)
                else:
                    path = options
                    straight = True

            # If it does go straight up/down, the path alternates
            if straight:
                while current_hex is not None:
                    for direction in path:
                        if current_hex is not None:
                            # print(self)  # To visualize generation
                            current_hex.terrain = "R"
                            roads.append(current_hex)
                            current_hex = current_hex.get_direction(direction)
            # Otherwise direction is constant
            else:
                while current_hex is not None:
                    # print(self)
                    current_hex.terrain = "R"
                    roads.append(current_hex)
                    current_hex = current_hex.get_direction(path)
        return roads

    def generate_buildings(self, roads):
        """Makes buildings along each road and each building"""
        # Overall list of possible spawning points
        structures = roads.copy()
        buildings = []

        # Starting with roads, but the list expands as buildings appear
        for structure in structures:
            # Checks for neighbors that aren't roads, buildings, or rivers
            tiles = structure.check_neighbors(("R", "W", "B"), True)
            for tile in tiles:
                if random() < self.build_chance:
                    # print(self)  # To visualize generation in real time
                    tile.terrain = "B"
                    buildings.append(tile)
                    structures.append(tile)
        return buildings


if __name__ == '__main__':
    # Running the program generates and prints a map
    map = Map(29, 29, kingdoms=4)
    # map.generate_forests()
    # map.generate_rivers()
    # roads = map.generate_roads()
    # map.generate_buildings(roads)
    print(map)
