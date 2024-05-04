import curses
import board
import time

BOARD_WIDTH = 10
BOARD_HEIGHT = 17

GAME_WINDOW_WIDTH = 2 * BOARD_WIDTH + 2
GAME_WINDOW_HEIGHT = BOARD_HEIGHT + 2

HELP_WINDOW_WIDTH = 18
HELP_WINDOW_HEIGHT = 7

STATUS_WINDOW_WIDTH = 18
STATUS_WINDOW_HEIGHT = 12

TITLE_HEIGHT = 0

LEFT_MARGIN = 3

TITLE_WIDTH = FOOTER_WIDTH = 50

def init_colors():
    """Init colors"""

    curses.init_pair(99, 8, curses.COLOR_BLACK) # 1 - grey
    curses.init_pair(98, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(97, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(96, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(95, curses.COLOR_BLACK, curses.COLOR_WHITE)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, 13) # 13 - pink
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)


def init_game_window():
    """Create and return game window"""

    window = curses.newwin(GAME_WINDOW_HEIGHT, GAME_WINDOW_WIDTH, TITLE_HEIGHT, LEFT_MARGIN)
    window.nodelay(True)
    window.keypad(1)

    return window


def init_status_window():
    """Create and return status window"""

    window = curses.newwin(STATUS_WINDOW_HEIGHT, STATUS_WINDOW_WIDTH, TITLE_HEIGHT, GAME_WINDOW_WIDTH + 5)
    return window


def draw_game_window(window):
    """Draw game window"""

    window.border()

    # draw board
    for a in range(BOARD_HEIGHT):
        for b in range(BOARD_WIDTH):
            if game_board.board[a][b] == 1:
                window.addstr(a + 1, 2 * b + 1, "  ", curses.color_pair(95))
            else:
                # draw net
                window.addstr(a + 1, 2 * b + 1, "  ", curses.color_pair(99))

    # draw current block
    for a in range(game_board.current_block.size()[0]):
        for b in range(game_board.current_block.size()[1]):
            if game_board.current_block.shape[a][b] == 1:
                x = 2 * game_board.current_block_pos[1] + 2 * b + 1
                y = game_board.current_block_pos[0] + a + 1
                window.addstr(y, x, "  ", curses.color_pair(game_board.current_block.color))

    if game_board.is_game_over():
        go_title = " GAME OVER "
        ag_title = " Enter - play again "

        window.addstr(int(GAME_WINDOW_HEIGHT*.4), (GAME_WINDOW_WIDTH-len(go_title))//2, go_title, curses.color_pair(95))
        window.addstr(int(GAME_WINDOW_HEIGHT*.5), (GAME_WINDOW_WIDTH-len(ag_title))//2, ag_title, curses.color_pair(95))

    if pause:
        p_title = " PAUSE "
        window.addstr(int(GAME_WINDOW_HEIGHT * .4), (GAME_WINDOW_WIDTH - len(p_title)) // 2, p_title,
                      curses.color_pair(95))

    window.refresh()


def draw_status_window(window):
    """Draw status window"""

    if game_board.is_game_over():
        return

    # hack: avoid clearing (blinking)
    for row in range(1, STATUS_WINDOW_HEIGHT - 1):
        window.addstr(row, 2, "".rjust(STATUS_WINDOW_WIDTH - 3, " "))

    window.border()

    window.addstr(1, 2, f"Score: {game_board.score}")
    window.addstr(2, 2, f"Lines: {game_board.lines}")
    window.addstr(3, 2, f"Level: {game_board.level}")
    # window.addstr(4, 2, f"Best Score: {game_board.best_score}")

    start_col = int(STATUS_WINDOW_WIDTH / 2 - game_board.next_block.size()[1])

    for row in range(game_board.next_block.size()[0]):
        for col in range(game_board.next_block.size()[1]):
            if game_board.next_block.shape[row][col] == 1:
                window.addstr(6 + row, start_col + 2 * col, "  ", curses.color_pair(game_board.next_block.color))

    window.refresh()
    pass


def draw_help_window():
    """Draw help window"""

    window = curses.newwin(HELP_WINDOW_HEIGHT, HELP_WINDOW_WIDTH, TITLE_HEIGHT + STATUS_WINDOW_HEIGHT,
                           GAME_WINDOW_WIDTH + 5)

    window.border()

    window.addstr(1, 2, "Quit — Q")
    window.addstr(2, 2, "Move — ← ↓ →")
    window.addstr(3, 2, "Drop — SPACE")
    window.addstr(4, 2, "Pause — P")
    window.addstr(5, 2, "Rotate — ↑")

    window.refresh()

def draw_footer():
    title = "BEST SCORE:"
    window = curses.newwin(1, FOOTER_WIDTH, TITLE_HEIGHT + GAME_WINDOW_HEIGHT + 1, LEFT_MARGIN)
    col_pos = int((GAME_WINDOW_WIDTH + STATUS_WINDOW_WIDTH - len(title) + 1) / 2)
    window.addstr(0, col_pos, title, curses.color_pair(98))
    window.addstr(0, col_pos + len(title) + 1, f"{game_board.best_score}", curses.color_pair(97))

    window.refresh()

pause = False

game_board = board.Board(BOARD_HEIGHT, BOARD_WIDTH)
game_board.start()

old_score = game_board.score

if __name__ == "__main__":
    try:
        scr = curses.initscr()
        curses.beep()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0)

        init_colors()
        draw_help_window()

        game_window = init_game_window()
        status_window = init_status_window()

        draw_game_window(game_window)
        draw_footer()
        draw_status_window(status_window)

        start = time.time()

        quit_game = False
        while not quit_game:
            key_event = game_window.getch()

            # hack: redraw it on resize
            if key_event == curses.KEY_RESIZE:
                draw_footer()
                draw_help_window()
                draw_game_window(game_window)

            if key_event == ord("q"):
                quit_game = True

            if not game_board.is_game_over():
                if not pause:
                    if time.time() - start >= 1 / game_board.level:
                        game_board.move_block("down")
                        start = time.time()

                    if key_event == curses.KEY_UP or key_event == ord("w") or key_event == ord("i"):
                        game_board.rotate_block()
                    elif key_event == curses.KEY_DOWN or key_event == ord("s") or key_event == ord("k"):
                        game_board.move_block("down")
                    elif key_event == curses.KEY_LEFT or key_event == ord("a") or key_event == ord("j"):
                        game_board.move_block("left")
                    elif key_event == curses.KEY_RIGHT or key_event == ord("d") or key_event == ord("l"):
                        game_board.move_block("right")
                    elif key_event == ord(" ") or key_event == 10:
                        game_board.drop()
                if key_event == ord("p"):
                    pause = not pause
                    game_window.nodelay(not pause)
            else:
                curses.beep()
                game_window.nodelay(False)
                if key_event == ord("\n"):
                    game_board.start()
                    game_window.nodelay(True)

            draw_game_window(game_window)

            if old_score != game_board.score:
                draw_status_window(status_window)
                draw_footer()
                old_score = game_board.score
    finally:
        curses.endwin()
