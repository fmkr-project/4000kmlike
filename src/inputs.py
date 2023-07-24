import pygame as pg

"""
Manage key inputs
"""
# TODO yaml file for controls


def handle_key_down(game, event):
    """Trigger action based on key press"""
    numerics = (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0)

    # Exit event
    if event.key == pg.K_ESCAPE:
        game.running = False
    
    # Fast forward
    if event.key == pg.K_f:
        game.fast_forward = not game.fast_forward
        game.logger.dump("Fast-forwarding") if game.fast_forward else game.logger.dump("Returning to normal speed")
    
    # Other connections - Menu
    if event.key == pg.K_r:
        if game.F_stmenu:
            game.F_stmenu = False
            game.F_rrmenu = True
            game.logger.dump("Connections menu now active")
        elif game.F_rrmenu:
            game.F_rrmenu = False
            game.F_stmenu = True
            game.logger.dump("Connections menu now closed")
    
    # Other connections - Choose direction
    if event.key in numerics and game.F_rrmenu:
        choice = numerics.index(event.key) + 1
        if game.main_window.can_choose(choice):
            game.main_window.submit_out(choice-1)
            game.logger.dump(f"In connections menu: chose option {choice}")

    # Timetable - Menu
    if event.key == pg.K_j:
        if game.F_stmenu:
            game.F_stmenu = False
            game.F_jikoku = True
            game.logger.dump("Timetable menu now active")
        elif game.F_jikoku and not game.F_choice:
            game.F_jikoku = False
            game.F_stmenu = True
            game.logger.dump("Timetable menu now closed")
    
    # Timetable - Go back to directions
    if event.key == pg.K_x and game.F_jikoku and game.F_choice:
        game.F_choice = False
        game.main_window.choice_dir = None
    
    # Timetable - Choose direction
    if event.key in numerics and game.F_jikoku and not game.F_choice:
        choice = numerics.index(event.key) + 1
        if game.main_window.can_choose(choice):
            game.F_choice = True
            game.main_window.choice_dir = numerics.index(event.key)
            game.logger.dump(f"In timetable menu: chose option {game.main_window.choice_dir + 1}")
    
    # Timetable - Control "arrow"
    if event.key == pg.K_UP and game.F_jikoku and game.F_choice:
        game.main_window.arpos -= 1
        if game.main_window.arpos < 0:
            game.main_window.arpos = 0
    if event.key == pg.K_DOWN and game.F_jikoku and game.F_choice:
        game.main_window.arpos += 1
        if game.main_window.arpos >= game.main_window.arbot:
            game.main_window.arpos = game.main_window.arbot
    
    # Timetable - Validate choice
    if event.key == pg.K_RETURN and game.F_jikoku and game.F_choice:
        game.main_window.submit_dt()
    

    # Train (stop) - Alight
    if event.key == pg.K_x and game.F_teisya:
        game.player.alight()