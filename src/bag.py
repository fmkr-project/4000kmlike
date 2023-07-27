class Bag():
    def __init__(self, player):
        self.player = player
        self.items = []
    

    def add(self, item):
        self.items.append(item)
        

    def remove(self, item):
        if item in self.items:
            del(self.items[self.items.index(item)])
        else:
            return