from collections import OrderedDict

import clock



class ServManager():
    def __init__(self, game):
        self.game = game
        self.servlist = {}

        # Initialize service list
        for serv in self.game.data.execute("select * from service").fetchall():
            # Buffer lines
            if serv[6] in (None, "") and serv[7] in (None, "") and serv[8] in (None, ""):
                self.game.logger.dump(f"[INFO] skipping service {serv[0]} as it has no data (buffer line)")
                continue
            new = Service(self, serv[0], serv[2], serv[3], serv[4],serv[5], serv[6], serv[7], serv[8], serv[9], serv[10])
            self.servlist[serv[0]] = new

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
            # TODO #3 yakou
            # TODO #2 use ordereddict structure
            for i in range(len(serv.jifun)-1):
                if serv.jifun[i] > serv.jifun[i+1]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: time {serv.jifun[i]} is before time {serv.jifun[i+1]}")

            for i in range(1, stopnum-1):
                if serv.jifun[1 + (i-1)*2] == serv.jifun[i*2]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: station id {serv.teisya[i]} has stopping time of 0 (@{serv.jifun[i*2]}), will be skipped")

        # Times check
        for serv in self.servlist.values():
            for time in serv.jifun:
                if (time // 10000 not in range(0,24) or (time % 10000) // 100 not in range(0,60) or time % 100 not in range(0,60)):
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: time {time} does not match format [h]hmmss")

        # Route check
        for serv in self.servlist.values():
            for sta in serv.keiro:
                if sta not in self.game.sta_manager.stalist_by_id():
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: unknown station id {sta}")
            for i in range(len(serv.keiro)-1):
                if not self.game.path_manager.has_path(serv.keiro[i], serv.keiro[i+1]):
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: no path between {serv.keiro[i]} and {serv.keiro[i+1]}")
                # Check if the route does not contain foot-only paths
                if True in [path.renraku for path in self.game.path_manager.get_paths(serv.keiro[i], serv.keiro[i+1])]:
                    self.game.logger.dump(f"[WARNING] in service of id {serv.id}: the path between {serv.keiro[i]} and {serv.keiro[i+1]} is not usable by a service")

        # Service continuity check
        for comp in self.get_comps():
            pass
    
    def get_serv_by_id(self, id):
        """Get a service by its id"""
        return self.servlist[id]
    
    def get_deptimes(self, start, end):
        """Given endpoints, get the list of every service going through them\n
        Result should be a dict with services as keys and their dep times as values (display format : no ss)."""
        depts = {}
        for serv in self.servlist.values():
            # Check if the path contains start followed by end
            for sta in range(len(serv.keiro)-1):
                if serv.keiro[sta] == start and serv.keiro[sta+1] == end:
                    try:
                        dep = serv.teisya.index(serv.keiro[sta])
                        depts[serv.id] = serv.jifun[2*dep] // 100               # Removing seconds
                    except:
                        # The Serv passes this station
                        pass
        sorted_depts = dict(sorted(depts.items(), key=lambda x: x[1]))
        return dict(zip(list(sorted_depts.keys()), list(sorted_depts.values())))


class Service():
    def __init__(self, mg, id, stype, nb, comp, name, path, stops, times, link, supp_fare):
        self.mg = mg
        self.mg.game.logger.dump(f"Creating service of id {id}")

        self.id = id
        self.syubetu = stype if stype != "" else None
        self.bangou = nb if nb != "" else None
        self.unyou = comp if comp != "" else None
        self.meisyo = name if name != "" else None
        
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
            # Convert from hmm / hhmm to hmmss / hhmmss
            for time in range(len(self.jifun)):
                if self.jifun[time] in range(0, 9999):    # TODO fix this
                    self.jifun[time] *= 100
        except:
            self.mg.game.logger.dump(f"[ERROR] in times: expected type list, found {times}")
        self.renketu = link
        self.yuuryou = supp_fare if supp_fare != "" else None

        # Calculated attributes
        self.path = self.mg.game.path_manager.build_path(self.keiro)
        self.ki = self.mg.game.sta_manager.get_sta_by_id(self.keiro[0])
        self.syu = self.mg.game.sta_manager.get_sta_by_id(self.keiro[-1])
        self.keiyu = self.mg.game.path_manager.build_linenames(self.mg.game.path_manager.build_path(self.keiro))

        # Construct dict of stops with A and D times
        # TODO sta that are passed
        self.staph = OrderedDict()
        for eki in self.keiro:
            # Initialize the OrderedDict with "empty" values
            self.staph[eki] = (-1, -1)
        for tei in range(len(self.teisya)):
            if tei == 0:
                self.staph[self.teisya[0]] = (-1, self.jifun[0])
            elif tei == len(self.teisya) - 1:
                self.staph[self.teisya[-1]] = (self.jifun[-1], -1)
            else:
                self.staph[self.teisya[tei]] = (self.jifun[1+(tei-1)*2], self.jifun[2*tei])
        # Keep track of stops and passages (for display purposes)
        self.staph_tei = OrderedDict()
        for eki in self.keiro:
            self.staph_tei[eki] = 'P'
        for tei in self.teisya:
            self.staph_tei[tei] = 'S'
        
        # Complete staph & compute average speeds
        self.hyotei = OrderedDict()
        for path in self.path:
            self.hyotei[path] = 0
        hyotei_sokudo = 0
        kukan_kyori = self.path[0].kyori
        tot_time = 0                                        # In seconds
        origin_path = 0                                     # Accumulator to store the first path of the current section
        s_jikoku = self.staph[self.teisya[0]][1]            # Section enter time
        for i in range(len(self.path)):
            # Add to the current computed section while the Service does not stop
            sec = (self.keiro[i], self.keiro[i+1])
            path = self.path[i]
            kukan_kyori += int(path.kyori * 1000)           # In m
            if sec[1] not in self.teisya and i != len(self.path)-1:
                continue

            # At this point, the Service comes to a stop, calculate the average speed
            tot_time = clock.sub_time(s_jikoku, self.staph[sec[1]][0])
            hyotei_sokudo = 3.6 * kukan_kyori / tot_time    # In km/h
            for p in range(origin_path, i+1):
                self.hyotei[self.path[p]] = hyotei_sokudo
            # Prepare for next computation
            kukan_kyori = 0
            s_jikoku = self.staph[sec[1]][1]                # -1 = terminus = no more computations
            origin_path = i+1
        
        # Compute passing times and add them to staph
        for i in range(len(self.path)):
            if self.staph[self.keiro[i+1]] == (-1, -1):
                syoyou = 1000 * self.path[i].kyori / (self.hyotei[self.path[i]] / 3.6)            # in s
                # Calculate passing time
                # TODO might want to create a function in the clock module
                pass_time = clock.tosec_hms(self.staph[self.keiro[i]][1]) + syoyou
                pass_time_normalized = int((pass_time // 3600) * 10000 + ((pass_time % 3600) // 60) * 100 + (pass_time % 60))
                self.staph[self.keiro[i+1]] = (pass_time_normalized, pass_time_normalized)
        
        # String representation (for display purposes)
        # TODO should not be None
        self.name_tostring = self.syubetu if self.syubetu is not None else "local"
        if self.name_tostring != "local":           # TODO placeholder
            self.name_tostring += f" <{self.meisyo}" if self.meisyo is not None else ""
            self.name_tostring += f" {self.bangou}>" if self.bangou is not None else ">" if self.meisyo is not None else ""
        self.name_tostring += f" for {self.mg.game.sta_manager.get_sta_by_id(self.keiro[-1]).name}"

    
    def get_next_section(self, sta):
        """Get section starting with specified station"""
        if sta.id == self.keiro[-1]:
            # Case when sta is the terminal station
            return None
        for i in range(len(self.keiro)-1):
            if self.keiro[i] == sta.id:
                return (self.mg.game.sta_manager.get_sta_by_id(self.keiro[i]), self.mg.game.sta_manager.get_sta_by_id(self.keiro[i+1]))
        return None

    def get_next_stop(self, id):
        """Get arrival time to the next Station & its id, where id is the id of the current Station."""
        if id not in self.keiro or id == self.syu.id:
            return None
        i = 0
        while self.keiro[i] != id:
            i += 1
        while self.staph_tei[self.keiro[i+1]] == 'P':
            i += 1
        return (self.keiro[i+1], self.staph[self.keiro[i+1]][0])

    def get_path_from_section(self, start, end):
        """Return the path of this Service between the specified endpoints"""
        for path in self.path:
            endpoints = (self.mg.game.sta_manager.get_sta_by_id(path.start), self.mg.game.sta_manager.get_sta_by_id(path.end))
            if (endpoints[0] == start and endpoints[1] == end) or (endpoints[1] == start and endpoints[0] == end):
                return path
        return None
        
    
    def _merge(self, serv2):
        """Internal function for service merging"""
        self.keiro.extend(serv2.keiro)
        del(self.teisya[-1])
        self.teisya.extend(serv2.teisya)
        self.jifun.extend(serv2.jifun)