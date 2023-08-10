import shop



class StaManager:
    def __init__(self, game):
        self.game = game
        self.stalist = {}
        
        # Initialize station list
        for sta in self.game.data.execute("select * from station").fetchall():
            new = Station(self, sta[0], sta[1], sta[3], sta[4], None)
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

    def is_busterm(self, sta_id):
        """Returns True if the given Station is a bus terminal, ie. has only roads departing from it"""
        data = [path[0] for path in self.game.data.execute(f"select road from path where (start = {sta_id} or end = {sta_id}) and onfootonly = 0").fetchall()]
        return data == [1 for _ in data]
    
    def build_optimes(self):
        """For every existing station, compute its opening times"""
        for sta in list(self.stalist.values()):
            if self.is_busterm(sta.id):             # TODO Bus stops don't close (for now)
                sta.open_time = (30000, 270000)
            else:
                dtimes = self.game.serv_manager._all_deptimes(sta.id)
                # Calculate opening times = 1 hour before / after the first / last Service and round to the nearest hour
                # Account for rollback at 0:00
                kai = min(dtimes) - 10000 if min(dtimes) - 10000 >= 30000 else min(dtimes) + 230000
                hei = max(dtimes) + 10000 if max(dtimes) + 10000 < 270000 else max(dtimes) - 230000
                sta.open_time = (kai - kai%10000, hei - hei%10000)



class Station:
    def __init__(self, mg, id, name, pic, stamp, coords):
        self.mg = mg
        self.mg.game.logger.dump(f"Creating station, {name}, of id {id}")

        # Low-level internals
        self.id = id
        self.name = name
        self.coords = coords

        # Gameplay internals
        self.shops = []
        self.open_time = None
        self.picture_exists = True if pic not in (None, "") else False
        self.picture_taken = False
        self.stamp_exists = True if stamp not in (None, "") else False
        self.stamp_taken = False