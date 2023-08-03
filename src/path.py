class PathManager():
    def __init__(self, game):
        self.game = game
        self.pathlist = {}

        for path in self.game.data.execute("select * from path").fetchall():
            if path[1] == "" and path[2] == "":
                self.game.logger.dump(f"[INFO] skipping path {path[0]} as it has no data (buffer line)")
            else:
                self.pathlist[path[0]] = Path(path[0], path[1], path[2], path[3], path[4], path[5], path[6], path[7])
    

    def integrity_check(self):
        """Check for anomalies in the pathlist"""
        self.game.logger.dump(f"[INFO] Running integrity check for paths")
        # Isolated stas
        for sta in self.game.sta_manager.stalist_by_id():
            if sta not in [path.start for path in self.pathlist.values()] + [path.end for path in self.pathlist.values()]:
                self.game.logger.dump(f"[WARNING] Station of id {sta} has no path going from/to it")
        
        # Redundancies
        for path1 in self.pathlist.values():
            for path2 in self.pathlist.values():
                if path1 == path2:
                    continue
                if (path1.start == path2.start and path1.end == path2.end) or (path1.end == path2.start and path1.start == path2.end):
                    if path1.kyori == path2.kyori:
                        self.game.logger.dump(f"[WARNING] Duplicate paths {path1.id} and {path2.id} of same length")
                    else:
                        self.game.logger.dump(f"[INFO] Paths {path1.id} and {path2.id} have the same route but different lengths (this might be intentional)")


    def has_path(self, start, end):
        """Check if a path exists between start and end"""
        for path in self.pathlist.values():
            if (path.start == start and path.end == end) or (path.end == start and path.start == end):
                return True
        return False

    def get_paths(self, start, end):
        """Return existing paths between specified endpoints"""
        res = []
        for path in self.pathlist.values():
            if (path.start == start and path.end == end) or (path.end == start and path.start == end):
                res.append(path)
        return res

    def get_path_by_id(self, path_id):
        """Return the path of given id"""
        return self.pathlist[path_id]
    

    def build_path(self, route):
        """Construct a list of paths between route start and end"""
        # Endpoints of route
        ki = route[0]; syu = route[-1]

        pathlist = []
        for i in range(len(route) - 1):
            for path in self.pathlist.values():
                if (path.start == route[i] and path.end == route[i+1]) or (path.end == route[i] and path.start == route[i+1]):
                    pathlist.append(path)
        return pathlist


    def build_linenames(self, pl):
        """Construct the list of route names from a path list"""
        linenames = []
        for path in pl:
            if path.rosen not in linenames:
                linenames.append(path.rosen)
        return linenames



class Path:
    def __init__(self, id, start, end, name, lg, onfoot, tarification, road):
        self.id = id
        self.start = start
        self.end = end
        self.rosen = name
        self.kyori = lg
        self.renraku = onfoot
        self.ftype = tarification
        
        self.is_road = road
        self.used = False