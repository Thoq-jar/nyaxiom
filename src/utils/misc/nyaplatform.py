from enum import Enum
from typing import final
import platform


@final
class Platform(Enum):
    LINUX = 0
    MACOS = 1
    WINDOWS = 2


def get_os() -> Platform:
    os = platform.system()
    if os == "Darwin":
        return Platform.MACOS
    elif os == "Windows":
        return Platform.WINDOWS
    else:
        return Platform.LINUX
