import sqlite3 as sql
import pygame as pg

import station
import path
import service
import log
import clock
import player
import window
import inputs



class Game:
    #RESDB_LOCATION = "res/game_data.db" # TODO #1 load other dbs
    RESDB_LOCATION = "res/tsugaru.db"
    TICKS_PER_SECOND = 60
    
    MAIN_WINDOW_DEFAULT_SIZE = (750, 750)

    def __init__(self):
        self.logger = log.Logger(self)
        self.logger.dump("Launching")
        
        # GUI
        pg.init()
        self.logger.dump("pygame initialized")
        self.logger.dump("Creating main window")
        self.main_window = window.MainWindow(self, self.MAIN_WINDOW_DEFAULT_SIZE[0], self.MAIN_WINDOW_DEFAULT_SIZE[1])

        # Flags
        self.F_stmenu = True        # Generic menu at a Station. Game always starts at a station
        self.F_jikoku = False       # Timetable menu
        self.F_choice = False       # Choice in timetable menu
        self.F_shinai = False       # City menu
        self.F_syanai = False       # Train menu

        # Gameplay internals
        self.fast_forward = False

        # Lower level internals
        self.logger.dump("Connecting to database")
        try:
            self.data = sql.connect(self.RESDB_LOCATION).cursor()
            # Control if all tables exist
            self.data.execute("select * from station")
            self.data.execute("select * from path")
            self.data.execute("select * from service")
        except sql.OperationalError:
            self.logger.dump("[CRITICAL] Database file could not be found")
            raise FileNotFoundError("Database file could not be found")

        self.clock = clock.Clock(self)

        self.sta_manager = station.StaManager(self)
        self.path_manager = path.PathManager(self)
        self.serv_manager = service.ServManager(self)

        print(self.serv_manager.get_deptimes(0,100))
        starting_sta = self.sta_manager.get_sta_by_id(0)    # TODO magic variable purge
        self.sta_manager.get_neighbors(0)
        self.player = player.Player(self, starting_sta)

        # Integrity checks
        self.logger.dump("Running integrity checks")
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

            # pg event management
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down(self, event)
        
            self.clock.pgclock.tick(self.TICKS_PER_SECOND)
        
        self.quit_game()
    

    def quit_game(self):
        """End game execution"""
        self.logger.dump("Now exiting game...")
        # DB connection closure
        try:
            self.data.close()
        except sql.ProgrammingError:
            self.logger.dump("[WARNING] Database is currently not accessible")
        pg.display.quit()
        pg.quit()
        self.logger.dump("Game exit complete.")


    def update(self):
        """Update game information when time changes"""
        pass