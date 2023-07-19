class PathManager():
    def __init__(self, game):
        self.game = game
        self.pathlist = []

        for path in self.game.data.execute("select * from path").fetchall():
            self.pathlist.append(Path(path[0], path[1], path[2], path[3], path[4]))
    

    def integrity_check(self):
        """Check for anomalies in the pathlist"""
        # Isolated stas
        for sta in self.game.sta_manager.stalist_by_id():
            if sta not in [path.start for path in self.pathlist] + [path.end for path in self.pathlist]:
                self.game.logger.dump(f"[WARNING] Station of id {sta} has no path going from/to it")
        
        # Redundancies
        for path1 in self.pathlist:
            for path2 in self.pathlist:
                if (path1.start == path2.start and path1.end == path2.end) or (path1.end == path2.start and path1.start == path2.end):
                    if path1.kyori == path2.kyori:
                        self.game.logger.dump(f"[WARNING] Duplicate paths {path1.id} and {path2.id} of same length")
                    else:
                        self.game.logger.dump(f"[INFO] Paths {path1.id} and {path2.id} have the same route but different lengths (this might be intentional)")


    def has_path(self, start, end):
        for path in self.pathlist:
            if (path.start == start and path.end == end) or (path.end == start and path.start == end):
                return True
        return False


class Path:
    def __init__(self, id, start, end, name, lg):
        self.id = id
        self.start = start
        self.end = end
        self.rosen = name
        self.kyori = lg
        
        self.used = False