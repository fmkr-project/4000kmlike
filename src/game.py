import sqlite3 as sql

import station
import path
import service
import log
import clock
import player



class Game:
    RESDB_LOCATION = "res/game_data.db"
    TICKS_PER_SECOND = 60

    def __init__(self):
        self.logger = log.Logger(self)
        self.data = sql.connect(self.RESDB_LOCATION).cursor()

        self.clock = clock.Clock(self)

        self.sta_manager = station.StaManager(self)
        self.path_manager = path.PathManager(self)
        self.serv_manager = service.ServManager(self)

        self.player = player.Player(self)

        # Integrity checks
        self.path_manager.integrity_check()
        self.serv_manager.integrity_check()



    def tick(self):
        """Operations on tick change"""
        self.clock.update()

    def run(self):
        """Main loop"""
        self.running = True

        while self.running:
            self.tick()
            self.clock.pgclock.tick(self.TICKS_PER_SECOND)
    

    def update(self):
        """Update game information when time changes"""
        pass