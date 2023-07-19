import sqlite3 as sql

import station
import path
import service
import log



class Game:
    RESDB_LOCATION = "res/game_data.db"


    def __init__(self):
        self.logger = log.Logger(self)
        self.data = sql.connect(self.RESDB_LOCATION).cursor()
        self.sta_manager = station.StaManager(self)
        self.path_manager = path.PathManager(self)
        self.serv_manager = service.ServManager(self)

        # Integrity checks
        self.path_manager.integrity_check()
        self.serv_manager.integrity_check()