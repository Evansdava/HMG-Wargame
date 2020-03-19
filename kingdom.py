from random import randint


class Kingdom():
    """Class governing the entities fighting for control of the map"""

    def __init__(self, name, field, territory, mil=10, admin=10, diplo=10):
        """Initialize with given size, default 1"""
        # Battlefield properties
        self.field = field
        self.die = field.len

        # Easy reference for modifiers
        self.half = self.field.len // 2
        self.third = self.field.len // 3
        self.fourth = self.field.len // 4
        self.eighth = self.field.len // 8

        # Int to determine stability
        # 0-2, resets to 0 at beginning of turn
        self.stable = 0

        # Dictionary of terrain types and the defense bonus they give
        self.terrains = {
            "W": self.fourth,
            "B": self.third,
            "R": -(self.eighth),
            "F": self.eighth,
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
            "mil": (sum([self._get_tile_value(tile, "mil")
                    for tile in self.territory]) + mil),
            "adm": (sum([self._get_tile_value(tile, "adm")
                    for tile in self.territory]) + admin),
            "dip": (sum([self._get_tile_value(tile, "dip")
                    for tile in self.territory]) + diplo)
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

    def _get_border_neighbors(self):
        """Return a set of non-owned tiles adjacent to borders"""
        neighbors = set()
        for tile in self.borders:
            for neighbor in tile.check_neighbors(tuple(self.terrains.keys())):
                if neighbor.owner != self:
                    neighbors.add(neighbor)
        return neighbors

    def _get_tile_value(self, tile, power):
        """Return the amount each type of tile increases powers"""
        # Default
        value = 1

        if power == "mil":
            if tile.terrain == "B":
                value = 3
            elif tile.terrain == "W":
                value = 2
            elif tile.terrain == "F":
                value = 2
        if power == "dip":
            if tile.terrain == "W":
                value = 4
            elif tile.terrain == "F":
                value = 3
            else:
                value = 0
        if power == "adm":
            if tile.terrain == "R":
                value = 4

        return value

    def _conquer(self, tile):
        """Helper function for changing owner of tile"""
        other = tile.owner
        if other is not None:
            other.territory.remove(tile)
            other.borders = other._get_borders()
            for power in other.powers.keys():
                other.powers[power] -= self._get_tile_value(tile, power)
        tile.owner = self
        self.territory.append(tile)
        for power in self.powers.keys():
            if self.powers[power] < self.die - 1:
                self.powers[power] += min(self._get_tile_value(tile, power),
                                          self.die - 1 - self.powers[power])
        self.borders = self._get_borders()

    def _choose_attack_target(self):
        """Determine which tile to attack"""
        tiles = list(self._get_border_neighbors())
        power = "mil" if self.powers["adm"] - len(self) > 5 else "adm"
        values = []
        for tile in tiles:
            value = self._get_tile_value(tile, power)
            other = tile.owner
            # Unowned tiles are desirable
            if other is None:
                value += 5
            # Tiles of a rival or ally's rival are desirable
            else:
                if other == self.rival:
                    value += 3
                if any([kingdom.rival == other for kingdom in self.allies]):
                    value += 3

                # Tiles of allies are not desirable
                if other in self.allies:
                    value -= 3

                # Tiles of weaker kingdoms are desirable
                if self._relative_threat(other) < 0:
                    value += 2
                # Tiles of stronger kingdoms are not
                else:
                    value -= 2

            # Tiles next to multiple border tiles are desirable
            if sum([int(neighbor.owner == self) for neighbor in
                    tile.get_neighbors() if neighbor is not None]) >= 2:
                value += 2

            values.append(value)
        return tiles[values.index(max(values))], max(values)

    def _get_stable_mods(self, other, power):
        """Helper function for determining modifier for stability"""
        stable_mod = (self.powers[power] // 4) * self.stable
        other_mod = (other.powers[power] // 4) * other.stable
        return stable_mod, other_mod

    def _calculate_threat(self, other):
        """Calculate the threat another kingdom poses to this one"""
        # Bigger kingdoms and more militarily powerful ones are threatening
        size_mod = len(other) - len(self)
        mil_mod = other.powers["mil"] - self.powers["mil"]

        # Allies pose less of a threat
        ally_mod = -self.fourth if other in self.allies else 0

        # Kingdoms with many shared borders are threatening
        border_mod = min(sum(2 for tile in self._get_border_neighbors()
                         if tile.owner == other), self.fourth)

        return size_mod + mil_mod + ally_mod + border_mod

    def _relative_threat(self, other):
        """Calculate the threat of a kingdom relative to this one's"""
        return other._calculate_threat(self) - self._calculate_threat(other)

    def _set_rival(self):
        """Set the most threatening kingdom as the rival"""
        kingdoms = self.field.kingdoms.copy()
        kingdoms.remove(self)
        threats = [self._calculate_threat(kingdom) for kingdom in kingdoms]
        greatest = sorted(threats, reverse=True)[0]
        self.rival = kingdoms[threats.index(greatest)]
        if self.rival in self.allies:
            self.allies.remove(self.rival)
            self.rival.allies.remove(self)

    def _choose_ally_target(self):
        """Choose a target to ally"""
        # Choose the most threatening kingdom that isn' a rival
        kingdoms = self.field.kingdoms.copy()
        kingdoms.remove(self)
        kingdoms.remove(self.rival)
        for ally in self.allies:
            if ally in kingdoms:
                kingdoms.remove(ally)
        threats = [self._calculate_threat(kingdom) for kingdom in kingdoms]
        if len(threats) > 0:
            ally = sorted(threats, reverse=True)[0]
            return kingdoms[threats.index(ally)]
        else:
            return None

    def conflict(self, other, power, self_mod=0, other_mod=0):
        """Run a conflict against another conflict of type with given mods"""
        # Stability represents a temporary improvement to base stats
        # Therefore it should always be calculated
        stable_mods = self._get_stable_mods(other, power)
        self_mod += stable_mods[0]
        other_mod += stable_mods[1]
        self_target = min(self.powers[power] + self_mod, self.die - 1)
        other_target = min(other.powers[power] + other_mod, self.die - 1)
        if self_target < 0:
            return False
        elif other_target < 0:
            return True
        # Loop until a value is returned
        while True:
            # Roll a die and add modifiers
            self_roll = randint(0, self.die)
            other_roll = randint(0, other.die)

            # Success is based on whichever power is used
            success = self_roll <= self_target
            other_success = other_roll <= other_target

            # If one is successful and the other isn't, there is a winner
            if success and not other_success:
                return True
            elif other_success and not success:
                return False

    def attack(self, tile):
        """Conduct a battle against another kingdom, trying to take tile"""
        other = tile.owner
        # If the other tile is unoccupied, there is no fight
        if other is None:
            self._conquer(tile)
            return True

        # To attack an ally, you need to win a diplomatic conflict
        allied = False
        if other in self.allies:
            allied = not self.conflict(other, "dip")
            if not allied:
                self.allies.remove(other)
                other.allies.remove(self)

        if not allied:
            terrain_mod = self.terrains[tile.terrain]
            battle = self.conflict(other, "mil", other_mod=terrain_mod)

            # If you win the military conflict, you get the tile
            if battle:
                self._conquer(tile)
                return True
            else:
                return False

    def ally(self, other):
        """Attempt to ally another kingdom"""
        # Other kingdoms are more willing to ally if you are stronger
        size_mod = len(self) - len(other)
        mil_mod = self.powers["mil"] - other.powers["mil"]

        # Sharing a rival is a large bonus
        rival_mod = self.third if self.rival == other.rival else 0

        # Sharing borders hurts chances at relations
        border_mod = min(len(self._get_border_neighbors()) * 2, self.fourth)

        self_mod = size_mod + mil_mod + rival_mod
        other_mod = border_mod

        alliance = self.conflict(other, "dip", self_mod, other_mod)
        if alliance and other.rival != self:
            if other not in self.allies:
                self.allies.append(other)
            if self not in other.allies:
                other.allies.append(self)
            return True
        else:
            return False

    def stabilize(self):
        """Stabilize kingdom to temporarily gain some of each power"""
        interference = self.rival.conflict(self, "adm")
        if interference:
            self.stable = 1
            if self.powers["adm"] < self.die - 1:
                self.powers["adm"] += min(2, self.die - self.powers["adm"] - 1)
            return False
        else:
            self.stable = 2
            if self.powers["adm"] < self.die - 1:
                self.powers["adm"] += min(5, self.die - self.powers["adm"] - 1)
            return True

    def take_turn(self):
        """Choose and take an action, reset modifiers, etc."""
        self.stable = 0
        self._set_rival()

        # Consider available options
        # If at least two kingdoms pose a significan threat, look for allies
        if sum([int(self._relative_threat(kingdom) > self.eighth)
               for kingdom in self.field.kingdoms if kingdom != self]) > 2:
            ally_chance = 15 if len(self.allies) == 0 else 10
            # Or stabilize
            stable_chance = 7
        else:
            ally_chance = 5
            stable_chance = 3

        # If all other kingdoms are allies or rivals, can't ally
        if len(self.allies) + 2 == len(self.field.kingdoms):
            ally_chance = -1

        # If high on admin, don't stabilize
        if self.powers["adm"] - len(self) > 15:
            stable_chance = 0

        # If low on admin, can't attack
        if self.powers["adm"] + 1 <= len(self):
            attack_chance = -1
            stable_chance = 10
        else:
            attack_chance = max(self._choose_attack_target()[1], 1)

        max_chance = attack_chance + ally_chance + stable_chance
        roll = randint(0, max_chance)
        if roll <= attack_chance:
            tile = self._choose_attack_target()[0]
            self.attack(tile)
        elif roll <= attack_chance + ally_chance:
            ally = self._choose_ally_target()
            if ally is not None:
                self.ally(ally)
        elif roll <= attack_chance + ally_chance + stable_chance:
            self.stabilize()


if __name__ == "__main__":
    from map import Map
    field = Map()
    print(field)
    king1 = Kingdom("1", field, [field[i] for i in range(20)], diplo=50)
    king2 = Kingdom("2", field, [field[i] for i in range(20, 30)])
    field.kingdoms.extend([king1, king2])
    print(field)
    print("Attack 1", king1.attack(field[21]))
    print("Attack 2", king2.attack(field[10]))
    print(field)
    print("Threat 1", king1._calculate_threat(king2))
    print("Threat 2", king2._calculate_threat(king1))
    print("Ally 1", king1.ally(king2))
    print(king1.allies)
    print(king2.allies)
    print("Ally 2", king2.ally(king1))
    king1._set_rival()
    king2._set_rival()
    print("Rival 1", king1.rival)
    print("Rival 2", king2.rival)
    print("Stable 1", king1.stabilize())
    print("Stable 2", king2.stabilize())
    print("Stability 1", king1.stable)
    print("Stability 2", king2.stable)
    # print(king1.half)
    # print(king1.third)
    # print(king1.fourth)
    # print(king1.eighth)
