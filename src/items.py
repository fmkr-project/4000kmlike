class ItemManager():
    def __init__(self, game):
        self.game = game
        self.itemlist = {}

        items = self.game.data.execute("select * from item").fetchall()
        for item in items:
            if item[2] == "consumable2":
                self.itemlist[item[0]] = Consumable2(item[0], item[1], item[2], item[3])
            elif item[2] == "consumable1":
                self.itemlist[item[0]] = Consumable1(item[0], item[1], item[2], item[3])
            elif item[2] == "instant":
                self.itemlist[item[0]] = Instant(item[0], item[1], item[2], item[3])
            elif item[2] == "camera":
                self.itemlist[item[0]] = Camera(item[0], item[1], item[2])
            elif item[2] == "sdcard":
                self.itemlist[item[0]] = SDCard(item[0], item[1], item[2], item[3])
            elif item[2] == "stampbook":
                self.itemlist[item[0]] = StampBook(item[0], item[1], item[2], item[3])
            else:
                self.itemlist[item[0]] = Item(item[0], item[1], item[2])

    
    def get_item_by_id(self, id):
        """Returns the item corresponding to the given id"""
        return self.itemlist[id]

    def use_item(self, item):
        # TODO filter by item type
        if type(item) in (Instant, Consumable2):
            self.game.player.restore_hunger(item)
        elif type(item) is Consumable1:
            pass # TODO hp
            


class Item():
    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
    
    # ? TEMP
    def initial(self):
        return self.name[0] if self.name is not None else ""
    
    def is_usable(self):
        return type(self) in (Consumable2, Consumable1)


class Instant(Item):
    """Items that cannot be stored in the player's inventory"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val

class Consumable2(Item):
    """Items that restore hunger"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val

class Consumable1(Item):
    """Items that restore health"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val

class Camera(Item):
    def __init__(self, id, name, type):
        super().__init__(id, name, type)
        # TODO add camera attributes

class SDCard(Item):
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.capacity = val

class StampBook(Item):
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.capacity = val