import curses
import os

class FilePanel:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.files = []
        self.selected = 0
        self.update_list()

    def update_list(self):
        try:
            self.files = ['..'] + os.listdir(self.path)
            self.files.sort()
        except PermissionError:
            self.files = ['..']
        self.selected = 0

    def enter(self):
        target = self.files[self.selected]
        full_path = os.path.join(self.path, target)
        if os.path.isdir(full_path):
            self.path = os.path.abspath(full_path)
            self.update_list()

    def move(self, direction):
        self.selected = max(0, min(self.selected + direction, len(self.files) - 1))


def draw_panel(stdscr, panel, x, y, width, height, active):
    stdscr.attron(curses.A_REVERSE if active else curses.A_NORMAL)
    stdscr.addstr(y, x, panel.path[:width])
    stdscr.attroff(curses.A_REVERSE if active else curses.A_NORMAL)

    for i in range(height - 1):
        idx = i
        if idx >= len(panel.files):
            break
        file_name = panel.files[idx]
        if idx == panel.selected:
            stdscr.attron(curses.A_STANDOUT)
        stdscr.addstr(y + i + 1, x, file_name[:width])
        if idx == panel.selected:
            stdscr.attroff(curses.A_STANDOUT)


def main(stdscr):
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    left = FilePanel(os.getcwd())
    right = FilePanel(os.getcwd())
    active_left = True

    while True:
        stdscr.clear()
        mid = w // 2
        draw_panel(stdscr, left, 0, 0, mid - 1, h, active_left)
        draw_panel(stdscr, right, mid + 1, 0, w - mid - 1, h, not active_left)
        stdscr.refresh()

        key = stdscr.getch()
        active = left if active_left else right

        if key == curses.KEY_UP:
            active.move(-1)
        elif key == curses.KEY_DOWN:
            active.move(1)
        elif key in [curses.KEY_ENTER, ord('\n')]:
            active.enter()
        elif key == 9:  # Tab
            active_left = not active_left
        elif key == 27:  # ESC
            break


if __name__ == '__main__':
    curses.wrapper(main)
