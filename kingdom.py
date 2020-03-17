from map import Map
from random import randint


class Kingdom:
    """Class governing the entities fighting for control of the map"""

    def __init__(self, field, size=1, mil=0, admin=0, diplo=0):
        """Initialize with given size, default 1"""
        self.field = field
        self.die = field.len
        self.size = size
        self.military = size + mil
        self.admin = field.len // 4 - size + admin
        self.diplo = diplo

        # Dictionary of terrain types and the defense bonus they give
        self.terrains = {
            "W": self.die // 3,
            "B": self.die // 2,
            "R": -(self.die // 4),
            "F": self.die // 4,
            ".": 0
        }

    def attack(self, other, tile):
        """Conduct a battle against another kingdom, trying to take tile"""
        # Loop until a value is returned
        print(tile)
        while True:
            # Each roll a die and compare the results to military skills
            attack = randint(0, self.die) < self.military
            print('Attack:', attack)
            def_roll = randint(0, self.die) + self.terrains[tile.terrain]
            defense = def_roll < other.military
            print('Defense', defense)

            # If one is successful and the other isn't, they win
            if attack and not defense:
                tile.owner = self
                return True
            elif defense and not attack:
                return False


if __name__ == '__main__':
    field = Map()
    king1 = Kingdom(field, 20)
    king2 = Kingdom(field, 10)
    print(king1.attack(king2, field[0]))
