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

        self.shopmenu = None

        # "Arrow"
        self.artop = 0                      # Top boundary
        self.arbot = 0                      # Bottom boundary
        self.arpos = None                   # Current arrow position

    
    def tick(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        ### General purpose blits
        # Blit the day & time
        # TODO delete magic variables !!!
        self.screen.blit(self.genfont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.genfont.render(self.game.clock.format(self.game.clock.get_hms()), True, (255, 255, 255)), (10, 40))
        if self.game.fast_forward:
            self.screen.blit(self.genfont.render('F', True, (255, 255, 255)), (140, 25))

        # Blit the name of the player's position
        # TODO function to determine if sta & service data can be displayed
        if self.game.player.sta is not None and (self.game.F_stmenu or self.game.F_teisya or self.game.F_jikoku or self.game.F_rrmenu or self.shopmenu is not None):
            self.screen.blit(self.bigfont.render(f"@ {self.game.player.sta.name}", True, (255, 255, 255)), (10, 70))
        elif self.game.player.kukan is not None and (self.game.F_soukou or self.game.player.F_wlking):
            self.screen.blit(self.bigfont.render(f"{self.game.player.kukan[0].name} > {self.game.player.kukan[1].name}", True, (255, 255, 255)), (10, 70))
        
        # Blit player's other attributes
        self.screen.blit(self.genfont.render(f"{math.ceil(self.game.player.hp)}", True,(255, 255, 255)), (170, 10))
        self.screen.blit(self.genfont.render(f"{math.ceil(self.game.player.onaka)}", True,(255, 255, 255)), (170, 40))
        self.screen.blit(self.genfont.render(f"{self.game.player.cash}", True,(255, 255, 255)), (230, 25))

        # Blit the 9 first items of the player's Bag
        for i in range(9):
            if i < len(self.game.player.bag.items):
                self.screen.blit(self.genfont.render(f"{i}: {list(self.game.player.bag.items.keys())[i].initial()}", True, (255, 255, 255)), (680, 10 + 30 * i))

        ### Menu-specific blits
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
                self.screen.blit(self.genfont.render(f">> {self.game.player.kukan[1].name} in {math.ceil(self.game.player.walking_dist / 100) / 10:.1f} km", True, (255, 255, 255)), (10, 130))
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
            # Display station shops
            if self.game.player.sta.shops != []:
                for i in range(len(self.game.player.sta.shops)):
                    self.screen.blit(self.genfont.render(f"{i+1}: {self.game.player.sta.shops[i].name}", True, (255, 255, 255)), (350, 70 + 30*i))
        
        # Shop menu
        if self.shopmenu is not None:
            shop = self.game.player.sta.shops[self.shopmenu]
            # Display sold items
            for i in range(len(shop.syouhin)):
                self.screen.blit(self.genfont.render(f"{i+1}: {list(shop.syouhin.keys())[i].name} | {list(shop.syouhin.values())[i]}", True, (255, 255, 255)), (350, 10 + 30*i))
            # Blit additional line for exit instructions
            self.screen.blit(self.genfont.render("x: back to station menu", True, (255, 255, 255)), (350, 10 + 30*len(shop.syouhin)))

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
            self.arpos = None
        
        # Other connections menu
        if self.game.F_rrmenu:
            neighbors = self.game.sta_manager.get_neighbors(self.game.player.sta.id)
            self.neighbors = {}
            # Only include directions that can be accessed only on foot
            for dest in neighbors:
                paths = self.game.path_manager.get_paths(self.game.player.sta.id, dest)
                # Find shortest path
                shortest = paths[0]
                for path in paths:
                    if path.kyori < shortest.kyori:
                        shortest = path
                if path.renraku != 0 or path.kyori <= self.game.player.MAX_WALKABLE_DISTANCE:
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
            # Initialize arrow position on opening
            if self.arpos is None:
                deltas = [time - self.game.clock.get_hms() // 100 for time in list(self.dts.values())]
                for i in range(len(deltas)):
                    deltas[i] = 9999 if deltas[i] < 0 else deltas[i]
                self.arpos = deltas.index(min(deltas))

            for i in range(len(self.dts)):
                # TODO find a way to make tabulations work properly (or use a monospace font)
                self.screen.blit(self.genfont.render(f"{list(self.dts.values())[i]} > {self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[i]).syu.name}", True, (255, 255, 255)), (30, 250 + 30*i))
            # Display "arrow"
            self.screen.blit(self.genfont.render('•', True, (255, 255, 255)), (10, 250 + 30*self.arpos))
        else:
            self.arpos = None
        
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
        self.arpos = None
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
        # Get walking distance (~ shortest path)
        paths = self.game.path_manager.get_paths(self.game.player.sta.id, list(self.neighbors.keys())[choice])
        shortest = paths[0]
        for path in paths:
            if path.kyori < shortest.kyori:
                shortest = path
        self.game.player.walking_dist = int(path.kyori * 1000)
        # Reset attributes
        self.game.F_rrmenu = False
        self.game.F_stmenu = False
        self.game.logger.dump(f"Taking outside connection to {self.game.player.kukan[1].name}, rem. {self.game.player.walking_dist}")
        # Reset player flags
        self.game.player.next_at = None
        self.game.player.next_dt = None
        self.game.player.serv = None

    
    def submit_shop(self, choice):
        """Get to the corresponding shop menu"""
        if not self.game.F_stmenu:
            self.game.logger.dump("[WARNING] wrong menu for entering a shop (this should not happen)")
        self.game.F_stmenu = False
        self.shopmenu = choice
    
    def submit_buy(self, choice):
        """Buy the chosen item if the player has enough money"""
        if self.shopmenu is None:
            self.game.logger.dump("[WARNING] wrong menu for buying an item (this should not happen)")
        self.game.F_stmenu = True
        self.game.player.buy(self.game.player.sta.shops[self.shopmenu], choice)
        self.shopmenu = None
    
    def can_choose(self, tgt):
        """Check if the target choice in the timetable menu does not overflow"""
        if self.game.F_jikoku or self.game.F_rrmenu:
            return tgt in range(1, len(self.neighbors) + 1)
        if self.game.F_stmenu:
            return tgt in range(1, len(self.game.player.sta.shops) + 1)
        if self.shopmenu is not None:
            return tgt in range(1, len(self.game.player.sta.shops[self.shopmenu].syouhin) + 1)
    
    def close_shopmenu(self):
        """Leave shop and go back to station menu"""
        self.game.F_stmenu = True
        self.shopmenu = None