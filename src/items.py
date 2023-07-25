class Item():
    def __init__(self, player, id, name, type):
        self.player = player
        self.id = id
        self.name = name
        self.type = type
    
    # ? TEMP
    def initial(self):
        return self.name[0] if self.name is not None else ""


class Consumable2(Item):
    """Items that restore hunger"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val
    
    def use(self):
        pass


class Consumable1(Item):
    """Items that restore health"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val