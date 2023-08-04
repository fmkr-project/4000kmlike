import pygame as pg



def sub_time(start, end):
    """Return the difference between start and end in seconds"""
    start_hms = (start // 10000, (start % 10000) // 100, start % 100)
    end_hms = (end // 10000, (end % 10000) // 100, end % 100)
    return tosec(end_hms) - tosec(start_hms)

def tosec(timestamp):
    """Convert a timestamp in [h, m, s] format to seconds"""
    return 3600*timestamp[0] + 60*timestamp[1] + timestamp[2]

def tosec_hms(hms):
    """Convert a timestamp in hhmmss format to seconds"""
    if hms//10000 < 3:
        hms += 240000       # Cancel 0:00 rollback
    return 3600*(hms//10000) + 60*((hms%10000)//100) + hms%100


class Clock():
    TIME_TICK = 25
    TIME_TICK_ACCEL = 2
    TIME_TICK_SUPERACCEL = 1
    MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    INITIAL_DATE = (7, 1)
    INITIAL_TIME = (5, 0, 0)

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()
        
        # Tick memory
        self.ticks_since_timechange = 0

        self.month = 7
        self.day = 1
        self.weekday = 1
        self.season = None

        # TODO replace with initial values in production
        self.hour = 6
        self.minute = 0
        self.second = 0

    def set(self, h, m, s=0):
        """Set the time (hh:mm)"""
        self.hour = h
        self.minute = m
        self.second = s
    
    def format(self, timestamp):
        """Format a timestamp (hhmm or hhmmss format) into hh:mm:ss format"""
        if timestamp in range(0, 9999):
            # hhmm
            return f"{timestamp // 100:02}:{timestamp % 100:02}:00"
        elif timestamp in range(10000, 999999):
            # hhmmss, with rollback between 24:00 (0:00) and 26:59 (2:59)
            return f"{timestamp // 10000:02}:{timestamp % 10000 // 100:02}:{timestamp % 100:02}" if timestamp // 10000 < 24 else f"{timestamp // 10000 - 24:02}:{timestamp % 10000 // 100:02}:{timestamp % 100:02}"
    
    def get_hms(self):
        """Return the current time in hhmmss format"""
        return self.hour * 10000 + self.minute * 100 + self.second if self.hour >= 3 else (self.hour + 24) * 10000 + self.minute * 100 + self.second
    
    def tick(self):
        """Operations after a pygame tick"""
        self.ticks_since_timechange += 1
        corrected_tick = self.TIME_TICK_ACCEL if (self.game.fast_forward and not self.game.pass_night) or (not self.game.fast_forward and self.game.pass_night)\
                         else self.TIME_TICK_SUPERACCEL if self.game.fast_forward and self.game.pass_night else self.TIME_TICK

        # Update time
        if self.ticks_since_timechange >= corrected_tick:
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
                        self.weekday += 1
                        if self.weekday >= 8:
                            self.weekday = 0
                        if self.day >= self.MONTH_LENGTHS[self.month-1]:
                            self.day = 0
                            self.month += 1
                            if self.month >= 12:
                                self.month = 1
            # Operations on time update
            self.game.player.update()