import shop



class StaManager:
    def __init__(self, game):
        self.game = game
        self.stalist = {}
        
        # Initialize station list
        for sta in self.game.data.execute("select * from station").fetchall():
            new = Station(self, sta[0], sta[1], None)
            if sta[2] not in ("", None):
                try:
                    shops = eval(sta[2])
                    for shop_id in shops:
                        shop_data = self.game.data.execute(f"select * from shop_preset where id = {shop_id}").fetchone()
                        new.shops.append(shop.FixedShop(self.game, (shop_data[2], shop_data[3]), shop_data[1]))
                    self.game.logger.dump(f"Station {sta[1]} has {len(shops)} shop(s)")
                except SyntaxError or NameError:
                    self.game.logger.dump(f"[WARNING] on station id {sta[0]}: expected type int list for station shops, found {sta[2]}")
            else:
                self.game.logger.dump(f"Station {sta[1]} has no shops")
            self.stalist[sta[0]] = new
    
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

        # Low-level internals
        self.id = id
        self.name = name
        self.coords = coords

        # Gameplay internals
        self.shops = []