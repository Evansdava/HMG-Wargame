from random import randint
from math import ceil


class Kingdom():
    """Class governing the entities fighting for control of the map"""

    def __init__(self, name, field, territory, mil=0, admin=0, diplo=0):
        """Initialize with given size, default 1"""
        # Battlefield properties
        self.field = field
        self.die = field.len

        # Dictionary of terrain types and the defense bonus they give
        self.terrains = {
            "W": self.die // 3,
            "B": self.die // 2,
            "R": -(self.die // 4),
            "F": self.die // 4,
            ".": 0
        }

        self.name = name

        # List of controlled hexes
        self.territory = territory
        for tile in self.territory:
            tile.owner = self

        self.borders = self._get_borders()

        # Dict of integers used for various checks
        self.powers = {
            "mil": len(self) + mil,
            "adm": int(ceil(len(self) / 2)) + admin,
            "dip": diplo
        }

        # Start the game allies
        self.allies = []
        self.rival = None

    def __len__(self):
        return len(self.territory)

    def __str__(self):
        return self.name

    def _get_borders(self):
        """Return a list of tiles that are on the outer edge of the kingdom"""
        borders = []
        for tile in self.territory:
            for neighbor in tile.check_neighbors(tuple(self.terrains.keys())):
                if neighbor.owner != self:
                    borders.append(tile)
                    break
        return borders

    def conflict(self, other, power, self_mod=0, other_mod=0):
        """Run a conflict against another conflict of type with given mods"""
        if self.powers[power] + self_mod < 0:
            return False
        elif other.powers[power] + other_mod < 0:
            return True
        # Loop until a value is returned
        while True:
            # Roll a die and add modifiers
            self_roll = randint(0, self.die)
            other_roll = randint(0, other.die)

            # Success is based on whichever power is used
            success = self_roll <= self.powers[power] + self_mod
            other_success = other_roll <= other.powers[power] + other_mod

            # If one is successful and the other isn't, there is a winner
            if success and not other_success:
                return True
            elif other_success and not success:
                return False

    def _conquer(self, tile):
        """Helper function for changing owner of tile"""
        if tile.owner is not None:
            tile.owner.territory.remove(tile)
            tile.owner.borders = tile.owner._get_borders()
        tile.owner = self
        self.territory.append(tile)
        self.borders = self._get_borders()

    def attack(self, other, tile):
        """Conduct a battle against another kingdom, trying to take tile"""
        # If the other tile is unoccupied, there is no fight
        if other is None:
            self._conquer(tile)
            return True

        # To attack an ally, you need to win a diplomatic conflict
        allied = False
        if other in self.allies:
            allied = not self.conflict(other, 'dip')

        if not allied:
            terrain_mod = self.terrains[tile.terrain]
            battle = self.conflict(other, 'mil', other_mod=terrain_mod)

            # If you win the military conflict, you get the tile
            if battle:
                self._conquer(tile)
                return True
            else:
                return False

    def _get_border_neighbors(self):
        """Return a set of non-owned tiles adjacent to borders"""
        neighbors = set()
        for tile in self.borders:
            for neighbor in tile.check_neighbors(tuple(self.terrains.keys())):
                if neighbor.owner != self:
                    neighbors.add(neighbor)
        return neighbors

    def calculate_threat(self, other):
        """Calculate the threat another kingdom poses to this one"""
        # Bigger kingdoms and more militarily powerful ones are threatening
        size_mod = len(other) - len(self)
        mil_mod = other.powers['mil'] - self.powers['mil']

        # Allies pose less of a threat
        ally_mod = -self.die // 3 if other in self.allies else 0

        # Kingdoms with many shared borders are threatening
        border_mod = sum(2 for tile in self._get_border_neighbors()
                         if tile.owner == other)

        return size_mod + mil_mod + ally_mod + border_mod

    def ally(self, other):
        """Attempt to ally another kingdom"""
        # Other kingdoms are more willing to ally if you are stronger
        size_mod = len(self) - len(other)
        mil_mod = self.powers['mil'] - other.powers['mil']

        # Sharing a rival is a large bonus
        rival_mod = self.die // 2 if self.rival == other.rival else 0

        # Sharing borders hurts chances at relations
        border_mod = len(self._get_border_neighbors()) * -2

        total_mod = size_mod + mil_mod + rival_mod + border_mod

        alliance = self.conflict(other, 'dip', total_mod)
        if alliance:
            self.allies.append(other)
            other.allies.append(self)
            return True
        else:
            return False


if __name__ == '__main__':
    from map import Map
    field = Map()
    print(field)
    king1 = Kingdom("1", field, [field[i] for i in range(20)], diplo=50)
    king2 = Kingdom("2", field, [field[i] for i in range(20, 30)])
    print(field)
    print(king1.attack(king2, field[21]))
    print(field)
    print('Threat', king2.calculate_threat(king1))
    print('Threat', king1.calculate_threat(king2))
    print(king1.ally(king2))
    print(king2.ally(king1))
