import pygame as pg

"""
Manage key inputs
"""
# TODO yaml file for controls


def handle_key_down(game, event):
    """Trigger action based on key press"""
    numerics = (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0)
    if event.key == pg.K_ESCAPE:
        game.running = False
    if event.key == pg.K_j:
        if game.F_stmenu:
            game.F_stmenu = False
            game.F_jikoku = True
            game.logger.dump("Timetable menu now active")
        elif game.F_jikoku and not game.F_choice:
            game.F_jikoku = False
            game.F_stmenu = True
            game.logger.dump("Timetable menu now closed")
    if event.key in numerics:
        if game.F_jikoku and not game.F_choice:
            choice = numerics.index(event.key) + 1
            if game.main_window.can_choose(choice):
                game.F_choice = True
                game.main_window.choice = numerics.index(event.key)
                game.logger.dump(f"In timetable menu: chose option {game.main_window.choice + 1}")
    if event.key == pg.K_x:
        if game.F_jikoku and game.F_choice:
            game.F_choice = False
            game.main_window.choice = None