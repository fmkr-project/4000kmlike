class Player:
    def __init__(self, game):
        self.game = game
        self.cash = 50000
        self.inventory = 9 * [None]

        # Map attributes
        self.sta = None
        self.serv = None

        # Record attributes
        self.soukiro = 0
    

    def gameover(self):
        """Check if the player can no longer continue"""
        return self.cash <= 0