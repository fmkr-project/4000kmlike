class Player:
    def __init__(self, game, sta):
        self.game = game
        self.cash = 50000
        self.inventory = 9 * [None]

        # Map attributes
        # TODO save function
        # TODO case when sta is None (ie. serv is not None)
        self.sta = sta
        self.serv = None

        self.next_serv = None
        self.using_line = None

        # Record attributes
        self.soukiro = 0
    

    def update(self):
        pass

    def gameover(self):
        """Check if the player can no longer continue"""
        return self.cash <= 0