# from random import random


class Hex():
    """The class that governs individual hexes on the map"""

    def __init__(self, id_num, terrain, owner=None):
        """Initializes the hex, setting the id number and relations"""
        self.id = id_num
        self.terrain = terrain
        self.owner = owner
        self.BR = None  # Bottom Right
        self.MR = None  # Middle Right
        self.BL = None  # Bottom Left
        self.ML = None  # Middle Left
        self.TL = None  # Top Left
        self.TR = None  # Top Right

    def __str__(self):
        """Return a string representation of this hex by terrain"""
        return f"{self.terrain}{str(self.owner)}" if self.owner is not None\
            else f"{self.terrain}."

    def connect(self, side, other):
        """Change the references of two hexes to match each other

        Arguments:
            side - the side of this hex to form a connection
            other - hex object; the other hex with which to connect this one

        Returns: None
        """
        # Whichever side is given as an argument,
        # the opposite of `other` is connected
        if side == "ML":
            self.ML = other
            other.MR = self
        elif side == "TL":
            self.TL = other
            other.BR = self
        elif side == "TR":
            self.TR = other
            other.BL = self
        elif side == "MR":
            self.MR = other
            other.ML = self
        elif side == "BR":
            self.BR = other
            other.TL = self
        elif side == "BL":
            self.BL = other
            other.TR = self

    def get_neighbors(self):
        """Return a tuple of all adjacent tiles"""
        return (self.MR, self.BR, self.BL, self.ML, self.TL, self.TR)

    def check_neighbors(self, keys=("."), exclude=False):
        """Return list of neighbors of this hex that match a key.

        Arguments:
            keys - tuple of strings used to represent terrain in hexes
            exclude - bool; when True, results are inverted

        Returns: list
        """
        neighbors = []
        for tile in self.get_neighbors():
            if tile is None:
                # Include out-of-bounds areas if exclude and keys are default
                if exclude and keys == ("."):
                    neighbors.append(tile)
            else:
                if tile.terrain in keys and not exclude:
                    neighbors.append(tile)
                elif tile.terrain not in keys and exclude:
                    neighbors.append(tile)
        return neighbors

    def get_direction(self, dir):
        """Returns a tuple of neighbors in a certain direction.
        Or a single neighbor, if given a specific face.

        Argument:
            dir - string; u = up, d = down, r = right, l = left
                  and specific directions return themselves

        Returns: tuple of hexes in opposite directions with corresponding
                 strings or single hex, based on input
        """
        if dir == "u":
            return ((self.ML, "ML"), (self.TL, "TL"),
                    (self.TR, "TR"), (self.MR, "MR"))
        if dir == "d":
            return ((self.ML, "ML"), (self.BL, "BL"),
                    (self.BR, "BR"), (self.MR, "MR"))
        if dir == "r":
            return ((self.TR, "TR"), (self.MR, "ML"), (self.BR, "BR"))
        if dir == "l":
            return ((self.BL, "BL"), (self.ML, "ML"), (self.TL, "TL"))

        if dir == "MR":
            return self.MR
        if dir == "BR":
            return self.BR
        if dir == "BL":
            return self.BL
        if dir == "ML":
            return self.MR
        if dir == "TL":
            return self.TL
        if dir == "TR":
            return self.TR
