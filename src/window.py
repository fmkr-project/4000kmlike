import pygame as pg


class MainWindow():
    def __init__(self, game, width, height):
        self.game = game

        # Graphic variables
        self.dimensions = [width, height]
        self.halves = [self.dimensions[0] // 2, self.dimensions[1] // 2]
        self.screen = pg.display.set_mode(self.dimensions)

        self.genfont = pg.font.Font(None, 40)
        self.bigfont = pg.font.Font(None, 70)

        # Internals
        self.neighbors = None
        self.lines = None
        self.dests = None
        self.choice = None

    
    def update(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        # Blit the day & time
        # TODO delete magic variables !!!
        self.screen.blit(self.genfont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.genfont.render(f"{self.game.clock.hour}:{self.game.clock.minute}:{self.game.clock.second}", True, (255, 255, 255)), (10, 40))

        # Blit the name of the player's position
        # TODO support for case sta is None (ie. serv is not None)
        if self.game.player.sta is not None:
            self.screen.blit(self.bigfont.render(f"@ {self.game.player.sta.name}", True, (255, 255, 255)), (10, 70))
        elif self.game.player.serv is not None:
            pass

        # Station menu
        if self.game.F_stmenu:
            self.screen.blit(self.genfont.render(f"j: Timetable menu", True, (255, 255, 255)), (300, 10))
        
        # Timetable menu
        if self.game.F_jikoku:
            # Display every neighbor
            # TODO cases of overly large stations (should be ok with the current db)
            self.neighbors = self.game.sta_manager.get_neighbors(self.game.player.sta.id)
            self.lines = list(self.neighbors.values())
            self.dests = [self.game.sta_manager.get_sta_by_id(sta).name for sta in self.neighbors.keys()]
            for i in range(len(self.neighbors)):
                self.screen.blit(self.genfont.render(f"{i+1}: {self.lines[i]} for {self.dests[i]}", True, (255, 255, 255)), (300, 10 + 30*i))
        else:
            self.neighbors = None
            self.lines = None
            self.dests = None
        # TODO Arrow2D system
        if self.game.F_choice:
            # Display departure times in 2 columns
            self.endpoints = (self.game.player.sta.id, list(self.neighbors.keys())[self.choice])
            self.dts = self.game.serv_manager.get_deptimes(self.endpoints[0], self.endpoints[1])
            for i in range(len(self.dts)): # TODO account for current time
                # TODO find a way to make \t work
                self.screen.blit(self.genfont.render(f"{list(self.dts.values())[i]} > {self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[i]).syu.name}", True, (255, 255, 255)), (30, 150 + 30*i))

        pg.display.flip()

    
    def can_choose(self, tgt):
        """Check if the target choice in the timetable menu does not overflow"""
        return tgt in range(1, len(self.neighbors) + 1)