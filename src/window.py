import pygame as pg


class MainWindow():
    def __init__(self, game, width, height):
        self.game = game
        self.dimensions = [width, height]
        self.halves = [self.dimensions[0] // 2, self.dimensions[1] // 2]
        self.screen = pg.display.set_mode(self.dimensions)

        self.timefont = pg.font.Font(None, 40)
    
    def update(self):
        """Update the display"""
        # Clear the screen
        self.screen.fill((0, 0, 0))     # TODO bg color as class variable

        # Blit the day & time at the bottom of the screen
        self.screen.blit(self.timefont.render(f"{self.game.clock.day}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.timefont.render(f"{self.game.clock.hour}:{self.game.clock.minute}:{self.game.clock.second}", True, (255, 255, 255)), (10, 40))

        pg.display.flip()