import pygame as pg
import tkinter as tk
import tkinter.messagebox as msg
import math



class MainWindow():
    MIN_SIZE = (800, 600)                   # Minimum screen size
    RESERVED_HEIGHT = 400                   # Header + footer height
    DT_LINE_HEIGHT = 30
    AR_OFFSET = 60                          # Space between two columns in the dt menu
    DEFAULT_FONT = "res/YuGothB.ttc"

    MAX_DESTS = 6                           # Maximum number of destinations on one page

    # Window structure:

    ########################################################
    #                                                      #
    #           Header (time, commands) - 250px            #
    #                                                      #
    ########################################################
    #                                                      #
    #                                                      #
    #                                                      #
    #                                                      #
    #                                                      #
    #               Body (dt menu) - dynamic               #
    #                                                      #
    #                                                      #
    #                                                      #
    #                                                      #
    #                                                      #
    #                                                      #
    ########################################################
    #                                                      #
    #             Footer (ticket info) - 150px             #
    #                                                      #
    ########################################################


    def __init__(self, game, width, height):
        self.game = game

        # Graphic variables
        self.dimensions = [width, height]
        self.halves = [self.dimensions[0] // 2, self.dimensions[1] // 2]
        self.screen = pg.display.set_mode(self.dimensions, pg.RESIZABLE)

        self.genfont = pg.font.Font(self.DEFAULT_FONT, 28)               # General purpose font
        self.bigfont = pg.font.Font(self.DEFAULT_FONT, 55)               # Font for important information
        self.detfont = pg.font.Font(self.DEFAULT_FONT, 20)               # Font for less important details

        # Internals
        self.neighbors = None
        self.lines = None
        self.dests = None

        self.choice_dir = None              # Current direction choice
        self.choice_serv = None             # Current service choice

        self.shopmenu = None

        # TODO qwerty
        self.item_keys = "azertyuiop"

        self.dir_page = 0                   # Page on the directions menu

        # "Arrow"
        self.artop = 0                      # Top boundary
        self.arbot = 0                      # Bottom boundary
        self.arpos = None                   # Current arrow position

    
    def tick(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        # Recalculate screen size and ensure the window does not shrink under its minimum size
        self.dimensions = list(pg.display.get_surface().get_size())
        corrected = False   # True if dimensions will be adjusted
        if self.dimensions[0] < self.MIN_SIZE[0]:
            self.dimensions[0] = self.MIN_SIZE[0]
            corrected = True
        if self.dimensions[1] < self.MIN_SIZE[1]:
            self.dimensions[1] = self.MIN_SIZE[1]
            corrected = True
        if corrected:
            self.screen = pg.display.set_mode(self.dimensions, pg.RESIZABLE)

        ### General purpose blits
        # Set up aliases
        # TODO
        current_station = self.game.player.sta

        # Blit the day & time
        # TODO delete magic variables !!!
        self.screen.blit(self.genfont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.genfont.render(self.game.clock.format(self.game.clock.get_hms()), True, (255, 255, 255)), (10, 40))
        if self.game.fast_forward:
            self.screen.blit(self.genfont.render('F', True, (255, 255, 255)), (140, 10))
        if self.game.pass_night:
            self.screen.blit(self.genfont.render('¤', True, (255, 255, 255)), (140, 40))

        # Blit the name of the player's position
        # TODO function to determine if sta & service data can be displayed
        if current_station is not None and (self.game.F_stmenu or self.game.F_teisya or self.game.F_jikoku or self.game.F_rrmenu or self.game.F_action or self.shopmenu is not None):
            self.screen.blit(self.bigfont.render(f"@ {current_station.name}", True, (255, 255, 255)), (10, 70))
        elif self.game.player.kukan is not None and (self.game.F_soukou or self.game.player.F_wlking):
            self.screen.blit(self.bigfont.render(f"{self.game.player.kukan[0].name} > {self.game.player.kukan[1].name}", True, (255, 255, 255)), (10, 70))
        
        # Blit player's other attributes
        self.screen.blit(self.genfont.render(f"{math.ceil(self.game.player.hp)}", True,(255, 255, 255)), (200, 10))
        self.screen.blit(self.genfont.render(f"{math.ceil(self.game.player.onaka)}", True,(255, 255, 255)), (200, 40))
        self.screen.blit(self.genfont.render(f"{self.game.player.cash}", True,(255, 255, 255)), (255, 25))

        # Blit station attributes
        if current_station.picture_taken and not self.game.F_soukou:
            self.screen.blit(self.genfont.render('P', True, (255, 255, 255)), (170, 10))
        if current_station.stamp_taken and not self.game.F_soukou:
            self.screen.blit(self.genfont.render('S', True, (255, 255, 255)), (170, 40))

        # Blit the 9 first items of the player's Bag
        bag = self.game.player.bag
        nb_displayed_items = 0
        i = 0
        while nb_displayed_items <= 9 and i < len(bag.items):
            if bag.items[i].is_usable():
                self.screen.blit(self.genfont.render(f"{self.item_keys[nb_displayed_items]}: {bag.items[i].initial()}", True, (255, 255, 255)), (self.dimensions[0] - 85, 10 + 30 * nb_displayed_items))
                nb_displayed_items += 1
            i += 1

        # Blit current ticket information
        ticket = self.game.player.kippu
        if ticket is not None and len(ticket.keiro) > 1:
            if ticket.sub is None:
                ticket_info = f"{ticket.keiro[0].name} > {ticket.keiro[-1].name} ({ticket.unchin})"
            else:
                ticket_info = f"{ticket.keiro[0].name} > {ticket.keiro[-1].name} ({ticket.unchin}) + ({ticket.sub.unchin})"
            self.screen.blit(self.bigfont.render(ticket_info, True, (255, 255, 255)), (10, self.dimensions[1] - 150))
            # Cut the string to make it fit on screen
            rts = ticket.route_tostring().split(' ')
            rts = [f"{elt} " for elt in rts]            # Restore spaces
            wordlengths = [sum([self.genfont.metrics(letter)[0][4] for letter in word]) for word in rts]
            line = ""
            linelength = 0
            linenb = 0
            while rts != []:
                line += rts[0]
                linelength += wordlengths[0]
                del(rts[0], wordlengths[0])
                if rts == [] or linelength + wordlengths[0] > self.dimensions[0] - 20:
                    # Display the line when adding a new word would cause it to not fit on screen
                    self.screen.blit(self.genfont.render(f"{line}", True, (255, 255, 255)), (10, self.dimensions[1] - 95 + 28*linenb))      # TODO suppress magic variables
                    line = ""
                    linelength = 0
                    linenb += 1
        

        # If the player is waiting, no menu can be displayed
        if self.game.player.wait:
            self.screen.blit(self.genfont.render(f"({math.ceil(self.game.player.wait / 4)} min.)", True, (255, 255, 255)), (350, 40))
            pg.display.flip()
            return

        ### Menu-specific blits
        # Blit the Service that will be used
        next_serv = self.game.player.serv
        if next_serv is not None:
            self.screen.blit(self.genfont.render(f"{next_serv.name_tostring}", True, (255, 255, 255)), (10, 130))
            if (self.game.F_stmenu or self.game.F_jikoku or self.game.F_rrmenu or self.game.F_action or self.shopmenu is not None):
                # TODO miss departure when not in stmenu
                self.screen.blit(self.genfont.render(f"{next_serv.ki.name} > {next_serv.syu.name} | arr. {self.game.clock.format(next_serv.staph[current_station.id][0])}", True, (255, 255, 255)), (10, 160))
            elif self.game.F_teisya:
                self.screen.blit(self.genfont.render(f"{next_serv.ki.name} > {next_serv.syu.name} | dep. {self.game.clock.format(next_serv.staph[current_station.id][1])}", True, (255, 255, 255)), (10, 160))
                # TODO clean this
                next_stop = self.game.sta_manager.get_sta_by_id(self.game.player.serv.get_next_stop(current_station.id)[0])
                self.screen.blit(self.genfont.render(f"next {next_stop.name}", True, (255, 255, 255)), (10, 190))

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
            next_stop = self.game.sta_manager.get_sta_by_id(self.game.player.serv.get_next_stop(current_station.id)[0])
            next_stop_arr = self.game.player.serv.get_next_stop(current_station.id)[1]
            self.screen.blit(self.genfont.render(f"{ki.name} {self.game.clock.format(self.game.player.serv.staph[ki.id][1])} > {syu.name} {self.game.clock.format(self.game.player.serv.staph[syu.id][0])}", True, (255, 255, 255)), (10, 160))
            self.screen.blit(self.genfont.render(f"{next_stop.name}{' [term]' if next_stop == syu else ''} arr. {self.game.clock.format(next_stop_arr)}", True, (255, 255, 255)), (10, 190))
            if self.game.F_kousya:
                self.screen.blit(self.genfont.render("alight next", True, (255, 255, 255)), (10, 220))
            # Controls
            alight_str = "x: alight next" if not self.game.F_kousya else "x: cancel alight"
            self.screen.blit(self.genfont.render(alight_str, True, (255, 255, 255)), (350, 10))


        # Station menu
        if self.game.F_stmenu:
            self.screen.blit(self.genfont.render(f"j: timetable menu", True, (255, 255, 255)), (350, 10))
            self.screen.blit(self.genfont.render(f"g: other connections", True, (255, 255, 255)), (350, 40))
            self.screen.blit(self.genfont.render(f"d: actions menu", True, (255, 255, 255)), (350, 70))
            # Display station shops
            if current_station.shops != []:
                for i in range(len(current_station.shops)):
                    self.screen.blit(self.genfont.render(f"{i+1}: {current_station.shops[i].name}", True, (255, 255, 255)), (350, 100 + 30*i))
        
        # Actions menu
        if self.game.F_action:
            sta = self.game.player.sta
            y = 10
            if sta.picture_exists and not sta.picture_taken:
                self.screen.blit(self.genfont.render(f"c: take picture", True, (255, 255, 255)), (350, y))
                y += 30
            if sta.stamp_exists and not sta.stamp_taken:
                self.screen.blit(self.genfont.render(f"s: take stamp", True, (255, 255, 255)), (350, y))
                y += 30
            self.screen.blit(self.genfont.render(f"d: back to station menu", True, (255, 255, 255)), (350, y))

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
            neighbors = self.game.sta_manager.get_neighbors(current_station.id)
            self.neighbors = {}             # Store a dict of structure {destination: line name}
            self.paths = []                 # Store a list of associated paths
            # Only include directions not accessible only on foot
            for dest in neighbors:
                paths = self.game.path_manager.get_paths(current_station.id, dest)
                if [path.renraku for path in paths] != [1 for _ in paths]:
                    self.neighbors[dest] = neighbors[dest]
                    self.paths.append([path for path in paths if path.renraku == 0][0])
            self.lines = list(self.neighbors.values())
            self.dests = [self.game.sta_manager.get_sta_by_id(sta).name for sta in self.neighbors.keys()]
            
            # Blit text for every direction available
            first = self.dir_page * self.MAX_DESTS              # First destination position to be displayed
            on_page = min(len(self.neighbors), (self.dir_page + 1) * self.MAX_DESTS) - first                 # Number of dests displayed
            self.dir_nbpages = math.ceil(len(self.neighbors) / self.MAX_DESTS)

            for i in range(first, first + on_page):
                pos = i-first
                self.screen.blit(self.genfont.render(f"{pos+1}: {self.lines[i]} for {self.dests[i]}", True, (255, 255, 255)), (350, 10 + 30*pos))
            # Blit line for page switching
            if self.dir_nbpages > 1:
                self.screen.blit(self.genfont.render("m: more destinations", True, (255, 255, 255)), (350, 10 + 30 * on_page))
                more = 1            # The next line must be shifted down
            else:
                more = 0
            # Blit additional line for exit instructions
            if self.game.F_choice:
                self.screen.blit(self.genfont.render("x: back to directions", True, (255, 255, 255)), (350, 10 + 30 * (on_page + more)))
            else:
                self.screen.blit(self.genfont.render("j: back to main menu", True, (255, 255, 255)), (350, 10 + 30 * (on_page + more)))
        else:
            # Set attributes to default (null) values
            self.neighbors = None
            self.paths = None
            self.lines = None
            self.dests = None
            self.arbot = 0
            self.arpos = None
        
        # Other connections menu
        if self.game.F_rrmenu:
            neighbors = self.game.sta_manager.get_neighbors(current_station.id)
            self.neighbors = {}
            # Only include directions that can be accessed only on foot
            for dest in neighbors:
                paths = self.game.path_manager.get_paths(current_station.id, dest)
                # Find shortest path
                # TODO might cause problems on station couples with more than one usable path
                shortest = paths[0]
                for path in paths:
                    if path.kyori < shortest.kyori:
                        shortest = path
                if path.renraku != 0 or path.kyori <= self.game.player.MAX_WALKABLE_DISTANCE:
                    self.neighbors[dest] = neighbors[dest]
            self.dests = [self.game.sta_manager.get_sta_by_id(sta).name for sta in self.neighbors.keys()]
            # Blit text for every direction available
            first = self.dir_page * self.MAX_DESTS              # First destination position to be displayed
            on_page = min(len(self.neighbors), (self.dir_page + 1) * self.MAX_DESTS) - first                 # Number of dests displayed
            self.dir_nbpages = math.ceil(len(self.neighbors) / self.MAX_DESTS)

            for i in range(first, first + on_page):
                pos = i-first
                self.screen.blit(self.genfont.render(f"{pos+1}: {self.dests[i]}", True, (255, 255, 255)), (350, 10 + 30*pos))
            # Blit line for page switching
            if self.dir_nbpages > 1:
                self.screen.blit(self.genfont.render("m: more destinations", True, (255, 255, 255)), (350, 10 + 30 * on_page))
                more = 1            # The next line must be shifted down
            else:
                more = 0
            # Blit additional line for exit instructions
            self.screen.blit(self.genfont.render("g: back to main menu", True, (255, 255, 255)), (350, 10 + 30 * (on_page + more)))
        
        # Train menu (at a Station)
        if self.game.F_teisya:
            # Display commands
            self.screen.blit(self.genfont.render("x: alight", True, (255, 255, 255)), (350, 10))
        
        # Departure time (deptime) submenu
        if self.game.F_choice:
            # Display departure times in 2 columns
            self.endpoints = (current_station.id, list(self.neighbors.keys())[self.choice_dir])
            self.dts = self.game.serv_manager.get_deptimes(self.endpoints[0], self.endpoints[1])
            self.arbot = len(self.dts) - 1

            # Multi-column display
            # Compute maximum amount of dts in one column
            self.column_size = (self.dimensions[1] - self.RESERVED_HEIGHT) // self.DT_LINE_HEIGHT
            self.nb_columns = len(self.dts) // self.column_size if len(self.dts) % self.column_size else len(self.dts) // self.column_size - 1
            # TODO calculate column width, for now uses a placeholder value
            self.column_widths = []
            for i in range(self.nb_columns + 1):
                # Compute a string with the name of the longest terminal
                terms = [self.game.serv_manager.get_serv_by_id(serv).syu.name for serv in self.dts.keys()][self.column_size * i:min(self.column_size * (i+1), len(self.dts))]
                lengths = [sum([metric[4] for metric in self.genfont.metrics(term)]) for term in terms]
                self.column_widths.append(self.AR_OFFSET + max(lengths) + sum([metric[4] for metric in self.genfont.metrics("8888: ")]))

            # Initialize arrow position on opening
            if self.arpos is None:
                deltas = [time - self.game.clock.get_hms() // 100 for time in list(self.dts.values())]
                for i in range(len(deltas)):
                    deltas[i] = 9999 if deltas[i] < 0 else deltas[i]
                try:
                    self.arpos = deltas.index(min(deltas))
                except:
                    # Guard when there is no service to choose from
                    self.arpos = 0
            
            current_column = self.arpos // self.column_size

            # Only blit columns that fit into the screen
            running_widths = [sum(self.column_widths[current_column : i+current_column+1]) for i in range(len(self.column_widths) - current_column)]
            widths_toright = [sum(self.column_widths) - sum(self.column_widths[:i]) if sum(self.column_widths) - sum(self.column_widths[:i]) < self.dimensions[0]-10 else 0
                              for i in range(len(self.column_widths))]
            rightmost_column = widths_toright.index(max(widths_toright))

            for i in range(len(self.dts)):
                pos = i % self.column_size          # Arrow position
                col = i // self.column_size         # Column number
                # Correctly display times >= 0:00
                corrected_dt = list(self.dts.values())[i]
                corrected_dt = corrected_dt - 2400 if corrected_dt > 2359 else corrected_dt
                dt_text = f"{corrected_dt:04} > {self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[i]).syu.name}"
                
                # Case when all departures can fit
                if sum(self.column_widths) < self.dimensions[0]-10:
                    self.screen.blit(self.genfont.render(dt_text, True, (255, 255, 255)), (30 + sum(self.column_widths[ :col]), 250 + self.DT_LINE_HEIGHT * pos))
                    self.screen.blit(self.genfont.render('•', True, (255, 255, 255)), (10 + sum(self.column_widths[ :self.arpos//self.column_size]), 250 + self.DT_LINE_HEIGHT * (self.arpos % self.column_size)))
                # Case when all departures at the right of the "arrow" can fit
                elif max(running_widths) < self.dimensions[0]-10:
                    if col >= rightmost_column:
                        self.screen.blit(self.genfont.render(dt_text, True, (255, 255, 255)), (30 + sum(self.column_widths[rightmost_column : col]), 250 + self.DT_LINE_HEIGHT * pos))
                        self.screen.blit(self.genfont.render('•', True, (255, 255, 255)), (10 + sum(self.column_widths[rightmost_column : self.arpos//self.column_size]), 250 + self.DT_LINE_HEIGHT * (self.arpos % self.column_size)))
                else:
                    # Do not blit if the departure is to the left of the current column or to the right of the rightmost blittable column
                    if col in range(current_column, 1 + current_column + running_widths.index(max([width for width in running_widths if width < self.dimensions[0]-10]))):
                        self.screen.blit(self.genfont.render(dt_text, True, (255, 255, 255)), (30 + sum(self.column_widths[current_column : i//self.column_size]), 250 + self.DT_LINE_HEIGHT * pos))
                        self.screen.blit(self.genfont.render('•', True, (255, 255, 255)), (10 + sum(self.column_widths[current_column : self.arpos//self.column_size]), 250 + self.DT_LINE_HEIGHT * (self.arpos % self.column_size)))
            # Display "arrow"
        else:
            self.arpos = None
        
        # Pygame actions
        pg.display.flip()
    
    def submit_dt(self):
        """Save the chosen Service in the player's data"""
        if len(self.dts) == 0:
            # No such Services have been defined in the DB
            self.game.logger.dump("[INFORMATION] trying to use a non-existent deptime")
            return
        if not self.game.F_choice:
            self.game.logger.dump("[WARNING] trying to submit a deptime outside of the deptime menu (this should not happen)")
        self.game.player.path = self.paths[self.choice_dir]
        self.game.player.serv = self.game.serv_manager.get_serv_by_id(list(self.dts.keys())[self.arpos])
        self.game.player.next_at = self.game.player.serv.staph[self.game.player.sta.id][0]
        self.game.player.next_dt = self.game.player.serv.staph[self.game.player.sta.id][1]
        self.game.player.kukan = self.game.player.serv.get_next_section(self.game.player.sta)
        # Create ticket information if the player doesn't have one
        if self.game.player.kippu is None:
            self.game.player.create_ticket()

        # Reset attributes
        self.neighbors = None
        self.paths = None
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


class PauseMenu(tk.Toplevel):
    def __init__(self, game):
        # This is a Singleton
        self.game = game

        # Initialize window
        self.root = tk.Tk()
        self.root.title("4000kmlike")
        self.buttons = []
        self.buttons.append(tk.Button(self.root, text = "      resume      ", command = self.kill))
        self.buttons.append(tk.Button(self.root, text = "        load        "))#, command = lambda self: self.game.load())
        self.buttons.append(tk.Button(self.root, text = "        save        "))#, command = lambda self: self.game.save())
        self.buttons.append(tk.Button(self.root, text = "        exit        ", command = self.prompt))

        # Blit statistics
        stats = self.game.player.stats_tostring()
        substats = self.game.player.substats_tostring()
        for elt in range(len(stats)):
            tk.Label(self.root, text = stats[elt]).grid(row = elt, column = 0)
        for elt in range(len(substats)):
            tk.Label(self.root, text = substats[elt]).grid(row = elt, column = 2)
        for i in range(len(self.buttons)):
            self.buttons[i].grid(row = i, column = 1)

        self.root.mainloop()
    
    def prompt(self):
        """Asks the player for game exiting"""
        if msg.askyesno(title = "4000kmlike", message = "exit?"):
            self.kill()
            self.game.quit_game()
    
    def kill(self):
        """Destroy this window and resets the game's pause menu"""
        self.game.pause_menu = None
        self.root.destroy()