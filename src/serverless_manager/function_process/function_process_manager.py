import time
from typing import Callable, Dict, Any

from src.serverless_manager.function_process.function_process import FunctionProcessCommunicator


class FunctionProcessManager:
    """
    Manager of function process communicators.
    Responsible for cleanup
    """

    def __init__(self, max_idle_time: int = 6):
        self.max_idle_time = max_idle_time
        self.function_processes = []

    def _create_function_process(self, function: Callable):
        new_function_process = FunctionProcessCommunicator(function)
        self.function_processes.append(new_function_process)
        return new_function_process

    def get_available_endpoint(self, func: Callable) -> FunctionProcessCommunicator:
        """
        Get a non-busy endpoint that runs the func function
        :param func: The function of the endpoint
        """
        for function_process in self.function_processes:
            if function_process.func == func and not function_process.is_busy:
                return function_process
        return self._create_function_process(func)

    def close_idle_processes(self) -> None:
        """
        Closes endpoint processes that did not receive a new request in the last self.max_idle_time seconds
        """
        func_processes_copy = self.function_processes[::]
        for i in range(len(func_processes_copy) - 1, -1, -1):  # reverse iteration so we can remove items dynamically
            function_process = func_processes_copy[i]
            if time.time() - function_process.last_called > self.max_idle_time and not function_process.is_busy:
                function_process.terminate()
                self.function_processes.pop(i)

    def run_function_on_endpoint(self, func: Callable, kwargs: Dict[str, str]) -> Any:
        return self.get_available_endpoint(func).run(kwargs)
