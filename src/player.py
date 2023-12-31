import bag
import items
import ticket



class Player:
    WALKING_SPEED_KPH = 5
    WALKING_SPEED_PER_TURN = WALKING_SPEED_KPH / 3600 * 15 * 1000
    MAX_WALKABLE_DISTANCE = 20.          # in km

    HG_PER_TURN = 0.045
    HG_PER_TURN_WALK = 0.09
    HP_PER_TURN = 0.0002
    HP_PER_TURN_ACCEL = 0.03

    def __init__(self, game, sta):
        self.game = game

        # Player internals
        self.cash = 50000
        self.bag = bag.Bag(self)
        self.hp = 100
        self.onaka = 100
        # TODO shuyuken
        self.kippu = None
        self.shuyu = []

        # Map attributes
        # TODO save function
        # TODO case when sta is None (ie. serv is not None)
        self.sta = sta              # Current Station
        self.serv = None            # Current boarding Service
        self.kukan = (None, None)   # Current segment endpoints
        self.path = None            # Current path
        self.walking_dist = 0       # Remaining walking distance
        self.wait = 0               # Remaining waiting time

        self.next_serv = None       # Next used Service
        self.next_at = None         # Next arrival time
        self.next_dt = None         # Next departure time
        self.next_sta = None

        # Flags
        self.F_wlking = False

        # Record attributes
        self.ressya_record = 0      # Sum of the lengths of already taken paths
        self.bus_record = 0
        self.ressya_soukiro = 0     # Total distance travelled
        self.bus_soukiro = 0
        self.walked_dist = 0
        self.syasin = {}
        self.stamp = {}


    def update(self):
        """Update player properties on time change"""
        # Case when the player walks
        self.hp -= self.HP_PER_TURN
        self.onaka -= self.HG_PER_TURN
        if self.F_wlking:
            self.onaka -= self.HG_PER_TURN_WALK
            self.walking_dist -= self.WALKING_SPEED_PER_TURN
            if self.walking_dist <= 0:
                self.walking_dist = 0
                self.F_wlking = False
                # Update current Station
                self.sta = self.kukan[1]
                self.kukan = None
                self.game.F_stmenu = True
        
        # Internals check
        if self.wait > 0:
            self.wait -= 1
        if self.onaka < 0:
            self.onaka = 0
            self.hp -= self.HP_PER_TURN_ACCEL
        if self.onaka >= 100:
            self.onaka = 100
        if self.gameover():
            self.game.gameover()

    def tick(self):
        """Update player properties every tick"""
        # Night time operations
        if not self.game.F_soukou:
            stime = self.sta.open_time
            self.game.pass_night = False if self.game.clock.get_hms() in range(stime[0], stime[1]+1) else True
        # Case when the player is already boarding a Service
        # At this point, the player already owns a ticket
        if self.game.F_soukou:
            touchaku = self.serv.staph[self.kukan[1].id][0]
            # Arrival at a Station
            if self.game.clock.get_hms() >= touchaku:
                self.sta = self.kukan[1]
                self.kukan = self.serv.get_next_section(self.sta)
                if self.kukan is None or (self.game.F_kousya and self.serv.staph_tei[self.kukan[0].id] != 'P'):
                    self.alight()
                    return
                self.path = self.serv.get_path_from_section(self.kukan[0], self.kukan[1])
                # Update game flags on stop
                if self.serv.staph_tei[self.kukan[0].id] != 'P':
                    self.game.F_teisya = True
                    self.game.F_soukou = False
                else:
                    self.update_tickets()
        elif self.game.F_teisya:
            hassya = self.serv.staph[self.kukan[0].id][1] if self.serv.syu != self.kukan[0] else None
            # Departure from a Station
            if self.game.clock.get_hms() >= hassya:
                self.game.F_teisya = False
                self.game.F_soukou = True
                if not self.path.used:
                    self.path.used = True
                    record_mul = 1
                else:
                    record_mul = 0
                if self.serv.is_train:
                    self.ressya_soukiro += self.path.kyori
                    self.ressya_record += self.path.kyori * record_mul
                if self.serv.is_bus:
                    self.bus_soukiro += self.path.kyori
                    self.bus_record += self.path.kyori * record_mul
                # Round statistics to account for floating point errors
                self.ressya_soukiro = round(self.ressya_soukiro, 1)
                self.ressya_record = round(self.ressya_record, 1)
                self.bus_soukiro = round(self.bus_soukiro, 1)
                self.bus_record = round(self.bus_record, 1)
                
                self.update_tickets()
        else:
            # Arrival of a Service when the player waits at a Station
            if self.next_at is not None and self.game.clock.get_hms() >= self.next_at and self.game.clock.get_hms() <= self.next_dt:
                # Update Player properties
                self.next_at = None

                # Update game flags
                self.game.main_window.close_shopmenu()
                self.game.F_action = False
                self.game.F_stmenu = False
                self.game.F_jikoku = False
                self.game.F_rrmenu = False
                self.game.F_choice = False
                # TODO case F_shinai
                self.game.F_teisya = True
            
            # Departure of a Service when the player first boards it
            if self.next_dt is not None and self.game.clock.get_hms() >= self.next_dt and self.next_at is None:
                # Update Player properties
                self.next_dt = None

                # Update game flags
                self.game.F_soukou = True
                self.game.F_teisya = False
    
    def update_tickets(self):
        """Update current Ticket information on path change"""
        # Generate new Ticket if route endpoint is already in the ticket's path or tarification system changes.
        # TODO cases when a station appears twice in a route
        if self.kukan[1] in self.kippu.keiro:
            self.end_ticket()
            self.create_ticket()
        elif self.kippu.ftype != self.path.ftype:
            # Manage compatible tarification changes
            ftypes = {self.kippu.ftype, self.path.ftype}
            tochange = None
            for conv in self.game.data.execute("select * from cpt_tarifications;").fetchall():
                if eval(conv[0]) == ftypes:
                    tochange = conv[1]
            if tochange is not None:
                self.kippu.ftype = tochange
            else:
                self.end_ticket()
                self.create_ticket()
        self.kippu.incr(self.path)


    def alight(self):
        """Leave Service and go to current station"""
        self.serv = None
        self.next_at = None
        self.next_dt = None
        self.kukan = (None, None)

        # Update game flags
        self.game.F_stmenu = True
        self.game.F_jikoku = False
        self.game.F_choice = False
        self.game.F_shinai = False
        self.game.F_soukou = False
        self.game.F_teisya = False
        self.game.F_kousya = False


    def create_ticket(self):
        """Initialize a new Ticket"""
        # TODO simplify this
        self.kippu = ticket.StandardTicket(self, self.sta)
        if self.serv.yuuryou is not None:
            self.kippu.sub = ticket.SubTicket(self, self.serv.yuuryou)


    def end_ticket(self):
        """Finish using the current Ticket"""
        # TODO collection
        # Subtract the ticket(s) current fare from the player's money
        self.cash -= self.kippu.unchin
        if self.kippu.sub is not None:
            self.cash -= self.kippu.sub.unchin
        # Destroy the ticket
        # TODO there has to be a "cleaner" way
        self.kippu = None
    
    def waitfor(self, mins):
        """Wait for a specified amount of minutes"""
        self.wait += mins * 4       # In quarters of minutes


    ### Item functions
    def buy(self, shop, choice):
        """Check if the player can afford the item in the specified shop"""
        item = list(shop.syouhin.keys())[choice]
        price = list(shop.syouhin.values())[choice]
        if self.cash >= price:
            if type(item) is items.Instant:
                self.game.item_manager.use_item(item)
            else:
                self.bag.add(item)
            self.cash -= price
            self.game.logger.dump(f"Successfully bought item {item.name}")
        else:
            self.game.logger.dump(f"Not enough money to buy {item.name}")
        
    def use_item(self, item_pos):
        """Take an item from the Bag and use it"""
        if item_pos < len(self.bag.items):
            item = self.bag.items[item_pos]
            self.bag.remove(item)
            self.game.item_manager.use_item(item)
        
    def restore_hunger(self, item):
        """Apply the effects of a Consumable2 item"""
        old = self.onaka
        self.onaka += item.kaifuku
        if self.onaka >= 100:
            self.onaka = 100
        self.game.logger.dump(f"Restored {item.kaifuku} hunger (from {old} to {self.onaka})")

    def can_take_pictures(self):
        return self.bag.has_type(items.Camera) and self.bag.has_type(items.SDCard)

    def can_stamp(self):
        return self.bag.has_type(items.StampBook)


    ### Action functions
    def take_picture(self):
        # TODO Use first non-full SD card in bag
        if self.sta.picture_exists and not self.sta.picture_taken and self.can_take_pictures():
            self.sta.picture_taken = True
            # TODO record other attributes when taking pictures (camera, etc.)
            self.syasin[self.sta.id] = True
            self.waitfor(2)
        else:
            self.game.logger.dump("Cannot take pictures without a camera and a SD card!")
        self.game.F_action = False
        self.game.F_stmenu = True
    
    def take_stamp(self):
        if self.sta.stamp_exists and not self.sta.stamp_taken and self.can_stamp():
            self.sta.stamp_taken = True
            # TODO record other attributes when obtaining stamps
            self.stamp[self.sta.id] = True
            self.waitfor(1)
        else:
            self.game.logger.dump("Cannot get stamp without a stamp book!")
        self.game.F_action = False
        self.game.F_stmenu = True


    def gameover(self):
        """Check if the player can no longer continue"""
        return self.cash <= 0 or self.hp <= 0


    # Functions for pause menu statistics
    def stats_tostring(self):
        """Return a string representation of the player's main records"""
        return (f"bus: current {self.bus_record} km of {self.game.path_manager.bus_total_dist()} km, total {self.bus_soukiro} km",
                f"train: current {self.ressya_record} km of {self.game.path_manager.train_total_dist()} km, total {self.ressya_soukiro} km",
                f"all: current {self.bus_record + self.ressya_record} km of {round(self.game.path_manager.bus_total_dist() + self.game.path_manager.train_total_dist(), 1)} km, total {round(self.bus_soukiro + self.ressya_soukiro, 1)} km")

    def substats_tostring(self):
        """Return a string representation of the player's secondary records (stamps, etc.)"""
        return (f"stamps: collected {len(self.stamp)} out of {self.game.data.execute('select count(*) from station where has_stamp = 1;').fetchall()[0][0]}",
                f"pictures: taken {len(self.syasin)} out of {self.game.data.execute('select count(*) from station where has_picture = 1;').fetchall()[0][0]}")