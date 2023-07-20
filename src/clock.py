import pygame as pg



class Clock():
    TIME_TICK = 25
    TIME_TICK_ACCEL = 2
    MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()
        
        # Tick memory
        self.ticks_since_timechange = 0

        self.month = 7
        self.day = 1
        self.season = None

        self.hour = 5
        self.minute = 0
        self.second = 0

    def set(self, h, m, s=0):
        """Set the time (hh:mm)"""
        self.hour = h
        self.minute = m
        self.second = s
    
    def get_hms(self):
        """Return the current time in hhmmss format"""
        return self.hour * 10000 + self.minute * 100 + self.second
    
    def update(self):
        """Operations after a pygame tick"""
        self.ticks_since_timechange += 1

        # Update time
        if self.ticks_since_timechange >= self.TIME_TICK:
            self.ticks_since_timechange = 0
            self.second += 15
            if self.second >= 60:
                self.second = 0
                self.minute += 1
                if self.minute >= 60:
                    self.minute = 0
                    self.hour += 1
                    if self.hour >= 24:
                        self.hour = 0
                        self.day += 1
                        if self.day >= self.MONTH_LENGTHS[self.month-1]:
                            self.day = 0
                            self.month += 1
                            if self.month >= 12:
                                self.month = 1