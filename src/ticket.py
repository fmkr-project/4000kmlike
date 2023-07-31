import fare



class Ticket():
    def __init__(self, player):
        self.player = player

        # Internals
        self.kyori = 0          # Current distance traveled
        self.seigen = None      # Time limit, no limit (permanent pass) should be None

        # TODO collection (in Player)
    


class StandardTicket(Ticket):
    def __init__(self, player, origin):
        super().__init__(player)
        self.unchin = 0                     # Current fare
        self.keiro = []                     # Current route
        self.ftype = None                   # Current tarification system
        self.keiro.append(origin)
        self.ftype = player.path.ftype      # Current tarification system
        self.sub = None                     # Secondary ticket (Express, etc.)
    
    def incr(self, path):
        """Modify ticket status depending on the current used path"""
        self.kyori += path.kyori
        endpoints = (self.player.game.sta_manager.get_sta_by_id(path.start), self.player.game.sta_manager.get_sta_by_id(path.end))
        sec = (endpoints[0], endpoints[1]) if endpoints[0] == self.player.sta else (endpoints[1], endpoints[0])
        self.keiro.append(sec[1])
        # Assume same tarification system (check beforehand)
        self.search_fare()
        if self.sub is not None:
            self.sub.search_fare()
        self.calculate_deadline()

    def search_fare(self):
        """Search the current fare depending on the current tarification system"""
        try:
            self.unchin = fare.search_fare(self.kyori, self.ftype)
        except:
            # TODO this should not happen in production
            self.unchin = fare.search_fare(self.kyori, "chihou")

    def route_tostring(self):
        """Return a string representation of the current route"""
        res = "via: "
        for sta in self.keiro:
            res += f"{sta.name}. "
        return res[:-2]

    def calculate_deadline(self):
        """Calculate remaining days before ticket expiration"""
        # Same for every line
        return self.kyori // 200 + 1


class SubTicket(Ticket):
    def __init__(self, player, ftype):
        super().__init__(player)
        self.unchin = 0                     # Current fare
        self.ftype = ftype                  # Should be const
    
    def search_fare(self):
        """Search the current fare depending on the current tarification system"""
        # Should not fail.
        self.unchin = fare.search_fare(self.kyori, self.ftype)


class WideTicket(Ticket):
    def __init__(self, player):
        super().__init__(player)