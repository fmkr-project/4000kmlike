import pygame as pg

class Clock():
    TIME_TICK = 100
    TIME_TICK_ACCEL = 5

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()
        
        # Tick memory
        self.ticks_since_timechange = 0

        self.month = 0
        self.day = 0
        self.season = None

        self.hour = 0
        self.minute = 0

    def set(self, h, m):
        """Set the time (hh:mm)"""
        self.hour = h
        self.minute = m
    
    def update(self):
        """Operations after a pygame tick"""
        self.ticks_since_timechange += 1

        # Update time
        if self.ticks_since_timechange >= self.TIME_TICK:
            self.ticks_since_timechange = 0
            self.minute += 1
            if self.minute == 60:
                self.minute = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0
                    self.day += 1
                    if self.day == 31:
                        self.day = 1
                        self.month += 1
                        if self.month == 13:
                            self.month = 1