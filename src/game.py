import station
import sqlite3 as sql

class Game:
    DB_LOCATION = "res/game_data.db"
    def __init__(self):
        self.sta_manager = station.StaManager(self)
        self.data = sql.connect(self.DB_LOCATION).cursor()