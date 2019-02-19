import os.path
import logging
from typing import Tuple, List

from core.luna import LunaCode

log = logging.getLogger(__name__)


def load_patterns() -> List[Tuple[str, str]]:
    """
    Ищет скрипт init.lua и подгружает остальные скрипты. Пока так.

    :return: List[Tuple[имя паттерна, код паттерна]]
    """
    result = []
    init_script = 'init'
    p = LunaCode(init_script, _load_file(init_script))
    try:
        ls = p.globals.requirements_pattern
        for name in ls.values():  # AttributeError
            assert isinstance(name, str)
            try:
                result.append((name, _load_file(name)))
            except FileNotFoundError as e:
                log.error(e)
    except AttributeError:
        log.error('in %s.lua not found "requirements_pattern"', init_script)
    return result


def _load_file(name: str) -> str:
    with open(os.path.join('patterns', name + '.lua')) as f:
        return f.read()
