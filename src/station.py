class StaManager:
    def __init__(self, game):
        self.game = game
        self.stalist = []
        
        # Initialize station list
        for sta in self.game.data.execute("select * from station").fetchall():
            self.stalist.append(Station(sta[0], sta[1], None))
    
    def stalist_by_id(self):
        return [sta.id for sta in self.stalist]


class Station:
    def __init__(self, id, name, coords):
        self.id = id
        self.name = name
        self.coords = coords
