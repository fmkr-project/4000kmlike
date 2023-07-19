import sqlite3 as sql

import station
import service
import log


class Game:
    RESDB_LOCATION = "res/game_data.db"


    def __init__(self):
        self.logger = log.Logger(self)
        self.data = sql.connect(self.RESDB_LOCATION).cursor()
        self.sta_manager = station.StaManager(self)
        self.serv_manager = service.ServManager(self)

        # Integrity checks
        self.serv_manager.integrity_check()