import bag



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

        # Map attributes
        # TODO save function
        # TODO case when sta is None (ie. serv is not None)
        self.sta = sta              # Current Station
        self.serv = None            # Current boarding Service
        self.kukan = (None, None)   # Current segment endpoints
        self.walking_dist = 0       # Remaining walking distance

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
        if self.gameover():
            self.game.gameover()

    def tick(self):
        """Update player properties every tick"""
        # Case when the player is already boarding a Service
        if self.game.F_soukou:
            touchaku = self.serv.staph[self.kukan[1].id][0]
            # Arrival at a Station
            if self.game.clock.get_hms() >= touchaku:
                self.sta = self.kukan[1]
                self.game.F_teisya = True
                self.kukan = self.serv.get_next_section(self.sta)
                if self.kukan is None:
                    self.alight()
                    return
                # Update game flags
                self.game.F_teisya = True
                self.game.F_soukou = False
        elif self.game.F_teisya:
            hassya = self.serv.staph[self.kukan[0].id][1] if self.serv.syu != self.kukan[0] else None
            # Departure from a Station
            if self.game.clock.get_hms() >= hassya:
                self.game.F_teisya = False
                self.game.F_soukou = True
        else:
            # Arrival of a Service
            if self.next_at is not None and self.game.clock.get_hms() >= self.next_at and self.game.clock.get_hms() <= self.next_dt:
                # Update Player properties
                # TODO manage termini
                # TODO load new times
                self.next_at = None

                # Update game flags
                self.game.F_stmenu = False
                self.game.F_jikoku = False
                self.game.F_choice = False
                # TODO case F_shinai
                self.game.F_teisya = True
            
            # Departure of a Service
            if self.next_dt is not None and self.game.clock.get_hms() >= self.next_dt and self.next_at is None:
                # Update Player properties
                self.next_dt = None

                # Update game flags
                self.game.F_soukou = True
                self.game.F_teisya = False

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


    def gameover(self):
        """Check if the player can no longer continue"""
        return self.cash <= 0 or self.hp <= 0