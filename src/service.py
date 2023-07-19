class ServManager():
    def __init__(self, game):
        self.game = game
        self.servlist = []

        # Initialize service list
        for serv in self.game.data.execute("select * from service").fetchall():
            self.servlist.append(Service(self, serv[0], serv[1], serv[2], serv[3],serv[4], serv[5], serv[6], serv[7], serv[8]))

    def get_comps(self):
        """Get list of compositions"""
        return list(set([serv.unyou for serv in self.servlist]))

    def integrity_check(self):
        """Check for anomalies in the servlist"""
        self.game.logger.dump(f"[INFO] Running integrity check for services")
        # todo syubetu
        # Format check
        for serv in self.servlist:
            stanum = len(serv.keiro)
            if stanum <= 1:
                self.game.logger.dump(f"[WARNING] in service of id {serv.id}: path len is abnormal")
            if stanum < len(serv.teisya):
                self.game.logger.dump(f"[WARNING] in service of id {serv.id}: too many stops ({len(serv.stops)}) for path of len {stanum}")
            if len(serv.jifun) != 2 * (stanum - 1):
                self.game.logger.dump(f"[WARNING] in service of id {serv.id}: incorrect format for times, expected [D, A, D, ... A, D, A]")
            
            # times in ascending order
            for i in range(len(serv.jifun)-1):
                if serv.jifun[i] > serv.jifun[i+1]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: time {serv.jifun[i]} is before time {serv.jifun[i+1]}")

        # Path check
        for serv in self.servlist:
            for sta in serv.keiro:
                if sta not in self.game.sta_manager.stalist_by_id():
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: unknown station id {sta}")

        # Service continuity check
        for comp in self.get_comps():
            pass


class Service():
    def __init__(self, mg, id, type, nb, comp, name, path, stops, times, link):
        self.mg = mg
        self.mg.game.logger.dump(f"Creating service of id {id}")

        self.id = id
        self.syubetu = type
        self.bangou = nb
        self.unyou = comp
        self.meisyo = name
        try:
            self.keiro = eval(path)
        except:
            self.mg.game.logger.dump(f"[ERROR] in path: expected type list, found {path}")
        
        try:
            self.teisya = eval(stops)
        except:
            self.mg.game.logger.dump(f"[ERROR] in stops: expected type list, found {stops}")
        
        try:
            self.jifun = eval(times)
        except:
            self.mg.game.logger.dump(f"[ERROR] in times: expected type list, found {times}")
        self.renketu = link
    
    def merge(self, serv2):
        self.keiro.extend(serv2.keiro)
        del(self.teisya[-1])
        self.teisya.extend(serv2.teisya)
        self.jifun.extend(serv2.jifun)