import sys
from .std_colors import BLUE, BOLD, NEUTRAL

show_progress_indicator_value = False
MAX_LENGTH = 120


def show_progress_indicator(value: bool) -> None:
    global show_progress_indicator_value  # pylint: disable=global-statement
    show_progress_indicator_value = value


def show_progress(progress: int, text: str) -> None:
    if not show_progress_indicator_value:
        return

    sys.stdout.write("".join(["\b \b" for _ in range(MAX_LENGTH)]))

    prefix = BLUE
    sys.stdout.write(prefix)

    sys.stdout.write(["-", "\\", "|", "/"][progress % 4])

    suffix = f" | {BOLD}{text}"
    sys.stdout.write(suffix[: MAX_LENGTH - len(prefix)] + NEUTRAL)

    sys.stdout.flush()
