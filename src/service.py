class ServManager():
    def __init__(self, game):
        self.game = game
        self.servlist = {}

        # Initialize service list
        for serv in self.game.data.execute("select * from service").fetchall():
            self.servlist[serv[0]] = Service(self, serv[0], serv[1], serv[2], serv[3],serv[4], serv[5], serv[6], serv[7], serv[8])

    def get_comps(self):
        """Get list of compositions"""
        return list(set([serv.unyou for serv in self.servlist.values()]))

    def integrity_check(self):
        """Check for anomalies in the servlist"""
        self.game.logger.dump(f"[INFO] Running integrity check for services")
        # todo syubetu
        # Format check
        for serv in self.servlist.values():
            stanum = len(serv.keiro)
            stopnum = len(serv.teisya)

            if stanum <= 1:
                self.game.logger.dump(f"[WARNING] in service of id {serv.id}: path len is abnormal")
            if stanum < stopnum:
                self.game.logger.dump(f"[WARNING] in service of id {serv.id}: too many stops ({len(serv.stops)}) for path of len {stanum}")
            if len(serv.jifun) != 2 * (stopnum - 1):
                self.game.logger.dump(f"[ERROR] in service of id {serv.id}: incorrect format for times, expected alternating A and D times")
            
            for sta in serv.teisya:
                if sta not in serv.keiro:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: station id {sta} does not belong to the path")
            
            # times in ascending order
            for i in range(len(serv.jifun)-1):
                if serv.jifun[i] > serv.jifun[i+1]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: time {serv.jifun[i]} is before time {serv.jifun[i+1]}")
            
            for i in range(1, stopnum-1):
                if serv.jifun[1 + (i-1)*2] == serv.jifun[i*2]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: station id {serv.teisya[i]} has stopping time of 0 (@{serv.jifun[i*2]}), will be skipped")

        # Path check
        for serv in self.servlist.values():
            for sta in serv.keiro:
                if sta not in self.game.sta_manager.stalist_by_id():
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: unknown station id {sta}")
            for i in range(len(serv.keiro)-1):
                if not self.game.path_manager.has_path(serv.keiro[i], serv.keiro[i+1]):
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: no path between {serv.keiro[i]} and {serv.keiro[i+1]}")
                # TODO bus etc

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

        # Calculated attributes
        self.path = self.mg.game.path_manager.build_path(self.keiro)
        self.ki = self.mg.game.sta_manager.get_sta_by_id(self.keiro[0])
        self.syu = self.mg.game.sta_manager.get_sta_by_id(self.keiro[-1])
        self.keiyu = self.mg.game.path_manager.build_linenames(self.mg.game.path_manager.build_path(self.keiro))

        
    
    def merge(self, serv2):
        self.keiro.extend(serv2.keiro)
        del(self.teisya[-1])
        self.teisya.extend(serv2.teisya)
        self.jifun.extend(serv2.jifun)