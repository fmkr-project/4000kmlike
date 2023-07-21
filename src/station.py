class StaManager:
    def __init__(self, game):
        self.game = game
        self.stalist = {}
        
        # Initialize station list
        for sta in self.game.data.execute("select * from station").fetchall():
            self.stalist[sta[0]] = Station(self, sta[0], sta[1], None)
    
    def stalist_by_id(self):
        """Get the list of station ids"""
        return self.stalist.keys()
    
    def get_sta_by_id(self, id):
        """Get a Station object by its id"""
        return self.stalist[id]
    
    def get_neighbors(self, id):
        """Return the list of all stas that have a path to the specified sta"""
        data = self.game.data.execute(f"select end, name from path where start = {id} union select start, name from path where end = {id}").fetchall()
        res = {}
        for path in data:
            # TODO There has to be a better way to do this
            res[path[0]] = path[1]
        return res


class Station:
    def __init__(self, mg, id, name, coords):
        self.mg = mg
        self.mg.game.logger.dump(f"Creating station, {name}, of id {id}")

        self.id = id
        self.name = name
        self.coords = coords
