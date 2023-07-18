class StaManager:
    def __init__(self, game):
        self.game = game
        self.list_of_stas = []

class Station:
    def __init__(self, id, name, coords):
        self.id = id
        self.name = name
        self.coords = coords
