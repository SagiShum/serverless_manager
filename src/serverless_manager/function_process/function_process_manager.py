import time
from typing import List, Callable, Dict

from src.serverless_manager.function_process.function_process import FunctionProcessCommunicator


class FunctionProcessManager:
    """
    Manager of function process communicators.
    Responsible for cleanup
    """
    def __init__(self, endpoint_services: List[Callable], max_idle_time: int = 6):
        self.services = endpoint_services
        self.max_idle_time = max_idle_time
        self.function_processes = []

    def _create_function_process(self, service: Callable):
        new_function_process = FunctionProcessCommunicator(service)
        self.function_processes.append(new_function_process)
        return new_function_process

    def get_available_endpoint(self, service: Callable) -> FunctionProcessCommunicator:
        for function_process in self.function_processes:
            if function_process.func == service and not function_process.is_busy:
                return function_process
        return self._create_function_process(service)

    def close_idle_processes(self):
        function_processes_copy = self.function_processes[::]
        for i in range(len(function_processes_copy)-1, -1, -1):  # reverse iteration so we can remove items dynamically
            function_process = function_processes_copy[i]
            if time.time() - function_process.last_called > self.max_idle_time and not function_process.is_busy:
                function_process.terminate()
                self.function_processes.pop(i)

    def run_service(self, service: Callable, kwargs: Dict[str, str]):
        return self.get_available_endpoint(service).run(kwargs)
