class ServManager():
    def __init__(self, game):
        self.game = game
        self.servlist = []

        # Initialize service list
        for serv in self.game.data.execute("select * from service").fetchall():
            self.servlist.append(Service(serv[0], serv[1], serv[2], serv[3],serv[4], serv[5], serv[6]))

    def get_comps(self):
        """Get list of compositions"""
        return list(set([serv.unyou for serv in self.servlist]))

    def integrity_check(self):
        """Check for anomalies in the servlist"""
        # todo syubetu
        # Service continuity check
        for comp in self.get_comps():
            pass


class Service():
    def __init__(self, id, type, name, comp, path, stops, times, link):
        self.id = id
        self.syubetu = type
        self.bangou = name
        self.unyou = comp
        self.keiro = path
        self.teisya = stops
        self.jifun = times
        self.renketu = link
        print(self)