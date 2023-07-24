import pygame as pg
import math


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

    
    def tick(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        # Blit the day & time
        # TODO delete magic variables !!!
        self.screen.blit(self.genfont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.genfont.render(self.game.clock.format(self.game.clock.get_hms()), True, (255, 255, 255)), (10, 40))
        if self.game.fast_forward:
            self.screen.blit(self.genfont.render('F', True, (255, 255, 255)), (150, 25))

        # Blit the name of the player's position
        # TODO support for case sta is None (ie. serv is not None)
        if self.game.player.sta is not None and (self.game.F_stmenu or self.game.F_teisya or self.game.F_jikoku or self.game.F_rrmenu):
            self.screen.blit(self.bigfont.render(f"@ {self.game.player.sta.name}", True, (255, 255, 255)), (10, 70))
        elif self.game.player.kukan is not None and (self.game.F_soukou or self.game.player.F_wlking):
            self.screen.blit(self.bigfont.render(f"{self.game.player.kukan[0].name} > {self.game.player.kukan[1].name}", True, (255, 255, 255)), (10, 70))
        
        # Blit the Service that will be used
        next_serv = self.game.player.serv
        if next_serv is not None and (self.game.F_stmenu or self.game.F_jikoku or self.game.F_rrmenu):
            # TODO miss departure when not in stmenu
            self.screen.blit(self.genfont.render(f"{next_serv.ki.name} > {next_serv.syu.name} | arr. {self.game.clock.format(next_serv.staph[self.game.player.sta.id][0])}", True, (255, 255, 255)), (10, 130))
        elif next_serv is not None and self.game.F_teisya:
            self.screen.blit(self.genfont.render(f"{next_serv.ki.name} > {next_serv.syu.name} | dep. {self.game.clock.format(next_serv.staph[self.game.player.sta.id][1])}", True, (255, 255, 255)), (10, 130))
            self.screen.blit(self.genfont.render(f"next {self.game.player.kukan[1].name}", True, (255, 255, 255)), (10, 160))

        # Blit information when walking
        if self.game.player.F_wlking:
            if self.game.player.walking_dist >= 1000:
                self.screen.blit(self.genfont.render(f">> {self.game.player.kukan[1].name} in {math.ceil(self.game.player.walking_dist / 100) / 10 * 1000} km", True, (255, 255, 255)), (10, 130))
            else:
                self.screen.blit(self.genfont.render(f">> {self.game.player.kukan[1].name} in {math.ceil(self.game.player.walking_dist / 100) * 100} m", True, (255, 255, 255)), (10, 130))

        # Blit general information when boarding a Service
        if self.game.F_soukou:
            ki = self.game.player.serv.ki
            syu = self.game.player.serv.syu
            self.screen.blit(self.genfont.render(f"{ki.name} {self.game.clock.format(self.game.player.serv.staph[ki.id][1])} > {syu.name} {self.game.clock.format(self.game.player.serv.staph[syu.id][0])}", True, (255, 255, 255)), (10, 130))
            self.screen.blit(self.genfont.render(f"{self.game.player.kukan[1].name} arr. {self.game.clock.format(self.game.player.serv.staph[self.game.player.kukan[1].id][0])}", True, (255, 255, 255)), (10, 160))

        # Station menu
        if self.game.F_stmenu:
            self.screen.blit(self.genfont.render(f"j: timetable menu", True, (255, 255, 255)), (350, 10))
            self.screen.blit(self.genfont.render(f"r: other connections", True, (255, 255, 255)), (350, 40))
        
        # Timetable menu
        if self.game.F_jikoku:
            # Display every neighbor
            # TODO cases of overly large stations (should be ok with the current db)
            neighbors = self.game.sta_manager.get_neighbors(self.game.player.sta.id)
            self.neighbors = {}
            # Only include directions not accessible only on foot
            for dest in neighbors:
                paths = self.game.path_manager.get_paths(self.game.player.sta.id, dest)
                if [path.renraku for path in paths] != [1 for _ in paths]:
                    self.neighbors[dest] = neighbors[dest]
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
        
        # Other connections menu
        if self.game.F_rrmenu:
            neighbors = self.game.sta_manager.get_neighbors(self.game.player.sta.id)
            self.neighbors = {}
            # Only include directions that can be accessed only on foot
            for dest in neighbors:
                paths = self.game.path_manager.get_paths(self.game.player.sta.id, dest)
                if [path.renraku for path in paths] != [0 for _ in paths]:
                    self.neighbors[dest] = neighbors[dest]
            self.dests = [self.game.sta_manager.get_sta_by_id(sta).name for sta in self.neighbors.keys()]
            # Blit text for every direction available
            for i in range(len(self.neighbors)):
                self.screen.blit(self.genfont.render(f"{i+1}: {self.dests[i]}", True, (255, 255, 255)), (350, 10 + 30*i))
            # Blit additional line for exit instructions
            self.screen.blit(self.genfont.render("r: back to main menu", True, (255, 255, 255)), (350, 10 + 30*len(self.neighbors)))
        
        # Train menu (at a Station)
        if self.game.F_teisya:
            # Display commands
            self.screen.blit(self.genfont.render("x: alight", True, (255, 255, 255)), (350, 10))
        
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
        self.game.player.serv = self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[self.arpos])
        self.game.player.next_at = self.game.player.serv.staph[self.game.player.sta.id][0]
        self.game.player.next_dt = self.game.player.serv.staph[self.game.player.sta.id][1]
        next_sta_id = self.game.player.serv.teisya[self.game.player.serv.teisya.index(self.game.player.sta.id) + 1]
        # self.game.player.next_sta = self.game.sta_manager.get_sta_by_id(next_sta_id)
        self.game.player.kukan = (self.game.player.sta, self.game.sta_manager.get_sta_by_id(next_sta_id))
        # Reset attributes
        self.neighbors = None
        self.lines = None
        self.dests = None
        self.arbot = 0
        self.arpos = 0
        self.game.F_choice = False
        self.game.F_jikoku = False
        self.game.F_stmenu = True
        self.game.logger.dump(f"Next train: {self.game.player.serv.ki.name} [{self.game.player.serv.jifun[0]}] > {self.game.player.serv.syu.name} [{self.game.player.serv.jifun[-1]}], arr. {self.game.player.next_at // 100} dep. {self.game.player.next_dt // 100}")
        
    def submit_out(self, choice):
        """Save the chosen outside connection in the player's data"""
        if not self.game.F_rrmenu:
            self.game.logger.dump("[WARNING] wrong menu for submitting an outside connection (this should not happen)")
        self.game.player.kukan = (self.game.player.sta, self.game.sta_manager.get_sta_by_id(list(self.neighbors.keys())[choice]))
        self.game.player.F_wlking = True
        # Get walking distance (there should be only one foot-only path)
        paths = self.game.path_manager.get_paths(self.game.player.sta.id, list(self.neighbors.keys())[choice])
        self.game.player.walking_dist = int([path.kyori for path in paths if path.renraku == 1][0] * 1000)
        # Reset attributes
        self.game.F_rrmenu = False
        self.game.F_stmenu = False
        self.game.logger.dump(f"Taking outside connection to {self.game.player.kukan[1].name}, rem. {self.game.player.walking_dist}")
        # Reset player flags
        self.game.player.next_at = None
        self.game.player.next_dt = None
        self.game.player.serv = None
    
    def can_choose(self, tgt):
        """Check if the target choice in the timetable menu does not overflow"""
        return tgt in range(1, len(self.neighbors) + 1)