try:
    from static.scripts.python.map import Map
except ModuleNotFoundError:
    from map import Map


class GameRunner(object):
    def __init__(self, field):
        """Initialize a new game"""
        self.field = field
        self.kingdoms = self.field.kingdoms

    def remove_kingdom(self, kingdom):
        """Remove kingdom from the game"""
        self.field.kingdoms.remove(kingdom)
        for other_kingdom in self.field.kingdoms:
            if kingdom in other_kingdom.allies:
                other_kingdom.allies.remove(kingdom)

    def turn(self):
        """Run through a turn of the game"""
        for kingdom in self.kingdoms:
            if len(kingdom) > 0:
                kingdom.take_turn()
            else:
                self.remove_kingdom(kingdom)

        # Check if the game is over
        if len(self.field.kingdoms) <= 1:
            return False


if __name__ == '__main__':
    i_list = []
    for _ in range(30):
        field = Map(kingdoms=4)
        gr = GameRunner(field)
        i = 0
        while gr.turn() is not False:
            print(gr.field)
            for kingdom in gr.field.kingdoms:
                print("Kingdom", str(kingdom), "Size:", len(kingdom))
                print(f"ADM: {kingdom.powers['adm']}", end=" ")
                print(f"DIP: {kingdom.powers['dip']}", end=" ")
                print(f"MIL: {kingdom.powers['mil']}")
                print(f"Rival: {kingdom.rival}", end=" ")
                print(f"Allies: {[str(king) for king in kingdom.allies]}")
            i += 1
            if i >= 1500:
                break
        print(i, "rounds")
        i_list.append(i)
    print(sum(i_list) / len(i_list))
