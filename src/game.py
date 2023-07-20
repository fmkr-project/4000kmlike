import sqlite3 as sql
import pygame as pg

import station
import path
import service
import log
import clock
import player
import window



class Game:
    #RESDB_LOCATION = "res/game_data.db" # TODO #1 load other dbs
    RESDB_LOCATION = "res/tsugaru.db"
    TICKS_PER_SECOND = 60
    
    MAIN_WINDOW_DEFAULT_SIZE = (750, 750)

    def __init__(self):
        self.logger = log.Logger(self)
        
        # GUI
        pg.init()
        self.main_window = window.MainWindow(self, self.MAIN_WINDOW_DEFAULT_SIZE[0], self.MAIN_WINDOW_DEFAULT_SIZE[1])

        # Internals
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
        self.main_window.update()
        self.clock.update()

    def run(self):
        """Main loop"""
        # GUI initialization
        # self.main_window.run()

        self.running = True

        while self.running:
            self.tick()
            self.clock.pgclock.tick(self.TICKS_PER_SECOND)
    

    def update(self):
        """Update game information when time changes"""
        pass