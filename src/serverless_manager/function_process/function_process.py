import time
import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import Callable, Dict, Any


def service_function(func: Callable, connection: Connection):
    """
    IO loop function for running func with params from pipe
    :param func: function to run
    :param connection: pipe to parent process
    """
    while True:
        kwargs = connection.recv()
        res = func(**kwargs)
        connection.send(res)


class FunctionProcessCommunicator:
    """
    Object wrapper for communicating with a child process
    """
    def __init__(self, func: Callable) -> None:
        """
        initializes child process
        :param func: function to be run by child process
        """
        self.last_called = None
        self.is_busy = False
        self.func = func
        self._init_child_process()

    @property
    def pid(self) -> int:
        return self.process.pid

    def _init_child_process(self) -> None:
        self.parent_conn, child_conn = mp.Pipe()
        self.process = mp.Process(target=service_function, args=[self.func, child_conn])
        self.process.start()

    def terminate(self) -> None:
        self.process.terminate()

    def _run_endpoint_function(self, kwargs: Dict[str, Any]) -> Any:
        self.parent_conn.send(kwargs)
        return self.parent_conn.recv()

    def run(self, kwargs: Dict[str, Any]):
        """
        Passes down arguments from the server to the child process
        :param kwargs: argument dict from server
        :return: child process run result
        """
        self.is_busy = True
        self.last_called = time.time()
        res = self._run_endpoint_function(kwargs)
        self.is_busy = False
        return res
