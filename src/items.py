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
            else:
                self.itemlist[item[0]] = Item(item[0], item[1], item[2])

    
    def get_item_by_id(self, id):
        """Returns the item corresponding to the given id"""
        return self.itemlist[id]

    def use_item(self, item):
        # TODO filter by item type
        pass


class Item():
    def __init__(self, id, name, type):
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


class Consumable1(Item):
    """Items that restore health"""
    def __init__(self, id, name, type, val):
        super().__init__(id, name, type)
        self.kaifuku = val