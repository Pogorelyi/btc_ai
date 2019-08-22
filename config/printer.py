from colored import fg, bg, attr


class Printer:

    def __init__(self):
        self._reset = attr(0)

    def red(self, str):
        color = fg('red')
        print(color + str + self._reset)

    def green(self, str):
        color = fg('green')
        print(color + str + self._reset)

    def indiana(self, str):
        color = bg('indian_red_1a') + fg('white')
        print(color + str + self._reset)

    def info(self, str):
        color = bg('light_goldenrod_2c') + fg('black') + attr('bold')
        print(color + str + self._reset)

    def yellow_bold(self, str):
        color = attr('bold') + fg('yellow')
        print(color + str + self._reset)

    def yellow(self, str):
        color = fg('yellow')
        print(color + str + self._reset)

