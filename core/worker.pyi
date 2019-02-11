from multiprocessing import Queue
from typing import Callable, Any, Optional

DEFAULT_TIMEOUT = None  # type:float


class TaskWorker:
    func = None  # type:Callable  # todo
    args = None  # type:tuple
    timeout = None  # type:float

    def __init__(self, func: Callable[..., ...], args=(), timeout=DEFAULT_TIMEOUT): ...


class Workers:
    __q_in = None  # type:Queue
    __q_out = None  # type:Queue

    def __init__(self): ...

    def start(self): ...

    def stop(self): ...

    def add_task(self, task: TaskWorker): ...

    def get_result(self, timeout=DEFAULT_TIMEOUT) -> Optional[Any]: ...


def start_worker(q_in: Queue, q_out: Queue): ...


def process_worker(q_in: Queue, q_out: Queue): ...
