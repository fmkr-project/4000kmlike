import station
import sqlite3 as sql



class Game:
    RESDB_LOCATION = "res/game_data.db"


    def __init__(self):
        self.data = sql.connect(self.RESDB_LOCATION).cursor()
        self.sta_manager = station.StaManager(self)