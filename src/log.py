import time

class Logger():
    LOG_PATH = "."

    def __init__(self, game):
        self.game = game
        self.file = open(f"{self.LOG_PATH}/dump.txt", "w")
        self.epoch = time.time()
    
    def get_timestamp(self):
        """Return time since logger epoch"""
        return round(time.time() - self.epoch, 3)

    def dump(self, message):
        """Flush a message to the dump file"""
        self.file.write(f"[{time.strftime('%H.%M.%S')} @ {self.get_timestamp():.3f}] - {message}\n")
        self.file.flush()