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
        # TODO
        self.soukiro = 0
    

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
        if self.onaka < 0:
            self.onaka = 0
            self.hp -= self.HP_PER_TURN_ACCEL
        if self.onaka >= 100:
            self.onaka = 100
        if self.gameover():
            self.game.gameover()

    def tick(self):
        """Update player properties every tick"""
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
        elif self.game.F_teisya:
            hassya = self.serv.staph[self.kukan[0].id][1] if self.serv.syu != self.kukan[0] else None
            # Departure from a Station
            if self.game.clock.get_hms() >= hassya:
                self.game.F_teisya = False
                self.game.F_soukou = True
                self.update_tickets()
        else:
            # Arrival of a Service when the player waits at a Station
            if self.next_at is not None and self.game.clock.get_hms() >= self.next_at and self.game.clock.get_hms() <= self.next_dt:
                # Update Player properties
                # TODO load new times
                self.next_at = None

                # Update game flags
                self.game.F_stmenu = False
                self.game.F_jikoku = False
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


    def gameover(self):
        """Check if the player can no longer continue"""
        return self.cash <= 0 or self.hp <= 0