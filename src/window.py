import pygame as pg


class MainWindow():
    def __init__(self, game, width, height):
        self.game = game

        # Graphic variables
        self.dimensions = [width, height]
        self.halves = [self.dimensions[0] // 2, self.dimensions[1] // 2]
        self.screen = pg.display.set_mode(self.dimensions)

        self.genfont = pg.font.Font(None, 40)               # General purpose font
        self.bigfont = pg.font.Font(None, 70)               # Font for important information
        self.detfont = pg.font.Font(None, 25)               # Font for less important details

        # Internals
        self.neighbors = None
        self.lines = None
        self.dests = None

        self.choice_dir = None              # Current direction choice
        self.choice_serv = None             # Current service choice

        # "Arrow"
        self.artop = 0                      # Top boundary
        self.arbot = 0                      # Bottom boundary
        self.arpos = 0                      # Current arrow position

    
    def update(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        # Blit the day & time
        # TODO delete magic variables !!!
        self.screen.blit(self.genfont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.genfont.render(f"{self.game.clock.hour:02d}:{self.game.clock.minute:02d}:{self.game.clock.second:02d}", True, (255, 255, 255)), (10, 40))
        if self.game.fast_forward:
            self.screen.blit(self.genfont.render('F', True, (255, 255, 255)), (150, 25))

        # Blit the name of the player's position
        # TODO support for case sta is None (ie. serv is not None)
        if self.game.player.sta is not None:
            self.screen.blit(self.bigfont.render(f"@ {self.game.player.sta.name}", True, (255, 255, 255)), (10, 70))
        elif self.game.player.serv is not None:
            pass
        
        # Blit the Service that will be used
        next_serv = self.game.player.next_serv
        if next_serv is not None:
            self.screen.blit(self.genfont.render(f"{next_serv.ki.name} > {next_serv.syu.name} | dep. {next_serv.staph[self.game.player.sta.id][1]}", True, (255, 255, 255)), (10, 130))

        # Station menu
        if self.game.F_stmenu:
            self.screen.blit(self.genfont.render(f"j: timetable menu", True, (255, 255, 255)), (350, 10))
        
        # Timetable menu
        if self.game.F_jikoku:
            # Display every neighbor
            # TODO cases of overly large stations (should be ok with the current db)
            self.neighbors = self.game.sta_manager.get_neighbors(self.game.player.sta.id)
            self.lines = list(self.neighbors.values())
            self.dests = [self.game.sta_manager.get_sta_by_id(sta).name for sta in self.neighbors.keys()]
            # Blit text for every direction available
            for i in range(len(self.neighbors)):
                self.screen.blit(self.genfont.render(f"{i+1}: {self.lines[i]} for {self.dests[i]}", True, (255, 255, 255)), (350, 10 + 30*i))
            # Blit additional line for exit instructions
            if self.game.F_choice:
                self.screen.blit(self.genfont.render("x: back to directions", True, (255, 255, 255)), (350, 10 + 30*len(self.neighbors)))
            else:
                self.screen.blit(self.genfont.render("j: back to main menu", True, (255, 255, 255)), (350, 10 + 30*len(self.neighbors)))
        else:
            self.neighbors = None
            self.lines = None
            self.dests = None
            self.arbot = 0
            self.arpos = 0
        
        # Departure time (deptime) submenu
        if self.game.F_choice:
            # Display departure times in 2 columns
            self.endpoints = (self.game.player.sta.id, list(self.neighbors.keys())[self.choice_dir])
            self.dts = self.game.serv_manager.get_deptimes(self.endpoints[0], self.endpoints[1])
            self.arbot = len(self.dts) - 1
            for i in range(len(self.dts)): # TODO account for current time
                # TODO find a way to make tabulations work properly (or use a monospace font)
                self.screen.blit(self.genfont.render(f"{list(self.dts.values())[i]} > {self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[i]).syu.name}", True, (255, 255, 255)), (30, 250 + 30*i))
            # Display "arrow"
            self.screen.blit(self.genfont.render('•', True, (255, 255, 255)), (10, 250 + 30*self.arpos))
        
        # Pygame actions
        pg.display.flip()
    
    def submit_dt(self):
        """Save the chosen Service in the player's data"""
        if not self.game.F_choice:
            self.game.logger.dump("[WARNING] trying to submit a deptime outside of the deptime menu (this should not happen)")
        self.game.player.next_serv = self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[self.arpos])
        # Reset attributes
        self.neighbors = None
        self.lines = None
        self.dests = None
        self.arbot = 0
        self.arpos = 0
        self.game.F_choice = False
        self.game.F_jikoku = False
        self.game.F_stmenu = True
        self.game.logger.dump(f"Next train: {self.game.player.next_serv.ki.name} [{self.game.player.next_serv.jifun[0]}] > {self.game.player.next_serv.syu.name} [{self.game.player.next_serv.jifun[-1]}], dep. {self.game.player.next_serv.staph[self.game.player.sta.id][1]}")
        

    
    def can_choose(self, tgt):
        """Check if the target choice in the timetable menu does not overflow"""
        return tgt in range(1, len(self.neighbors) + 1)