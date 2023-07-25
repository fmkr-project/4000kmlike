class Bag():
    def __init__(self, player):
        self.player = player
        self.items = {}
    
    def add(self, item, qty = 1):
        if item not in self.items:
            self.items[item] = qty
        else:
            self.items[item] += qty

    def remove(self, item):
        if item in self.items:
            self.items[item] -= 1
        else:
            return