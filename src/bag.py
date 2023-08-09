import items



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
    

    def usable_items(self):
        return [item for item in self.items if type(item) in (items.Consumable2, items.Consumable1)]