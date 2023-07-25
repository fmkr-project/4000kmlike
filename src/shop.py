import items

class Shop():
    def __init__(self, game, preset, name):
        # TODO hours
        # TODO ekisoba
        
        self.game = game
        self.name = name
        
        # Internals
        # Error is caught in the Station object construction
        objects = [self.game.item_manager.get_item_by_id(item) for item in eval(preset[0])]
        self.syouhin = dict(zip(objects, eval(preset[1])))


class FixedShop(Shop):
    """Shops that have a fixed location"""
    def __init__(self, game, preset, name):
        super().__init__(game, preset, name)


class MovingShop(Shop):
    """Shops that don't have a fixed location"""
    def __init__(self, game, preset, name):
        super().__init__(game, preset, name)