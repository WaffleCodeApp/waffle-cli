import sys

from .std_colors import BLUE, BOLD, NEUTRAL

show_progress_bar_value = False
BAR_LENGTH = 40
MAX_LENGTH = 120


def show_progress_bar(value: bool) -> None:
    """setting progress bar visibility"""
    global show_progress_bar_value  # pylint: disable=global-statement
    show_progress_bar_value = value


def show_progress(current: int, maximum: int, text: str) -> None:
    """invoking the progress bar"""
    if not show_progress_bar_value:
        return

    sys.stdout.write("".join(["\b \b" for _ in range(MAX_LENGTH)]))

    prefix = f"{int(100 * current / maximum)}% "
    sys.stdout.write(BLUE + prefix)

    for i in range(BAR_LENGTH):
        if i < int(BAR_LENGTH * current / maximum):
            sys.stdout.write("#")
        elif i == int(BAR_LENGTH * current / maximum):
            sys.stdout.write(["-", "\\", "|", "/"][current % 4])
        else:
            sys.stdout.write(".")

    suffix = f" {current} / {maximum} | {BOLD}{text}"
    sys.stdout.write(suffix[: MAX_LENGTH - BAR_LENGTH - len(prefix)] + NEUTRAL)

    sys.stdout.flush()
