import fare



class Ticket():
    def __init__(self, player):
        self.player = player

        # Internals
        self.unchin = 0         # Current fare
        self.ftype = None       # Current tarification system
        self.kyori = 0          # Current distance traveled
        self.keiro = []         # Current route
        self.seigen = None      # Time limit, no limit should be None

        # TODO collection (in Player)
    


class StandardTicket(Ticket):
    def __init__(self, player, origin):
        super().__init__(player)
        self.keiro.append(origin)
    
    def incr(self, sec):
        """Modify ticket status depending on the current section"""
        path = self.player.game.path_manager.get_paths(sec[0].id, sec[1].id)[0]       # Assume shortest route
        self.kyori += path.kyori
        self.keiro.append(sec[1])
        # TODO manage tarification systems correctly
        self.ftype = "chihou"
        self.search_fare()
        self.calculate_deadline()

    def search_fare(self):
        """Search the current fare depending on the current tarification system"""
        try:
            self.unchin = fare.search_fare(self.kyori, self.ftype)
        except:
            self.unchin = fare.search_fare(self.kyori, "chihou")

    def route_tostring(self):
        """Return a string representation of the current route"""
        res = "via: "
        for sta in self.keiro:
            res += f"{sta.name}. "
        return res[:-2]

    def calculate_deadline(self):
        """Calculate remaining days before ticket expiration"""
        return 1 # TODO


class WideTicket(Ticket):
    def __init__(self, player):
        super().__init__(player)