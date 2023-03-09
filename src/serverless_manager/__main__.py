from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from services import sleep_and_sum

from src.serverless_manager.function_process.function_process_manager import FunctionProcessManager

app = Flask(__name__)
services = [sleep_and_sum]
services_map = {func.__name__: func for func in services}
process_manager = FunctionProcessManager(services)
request_count = 0


@app.route('/<string:service_name>', methods=['GET'])
def run_serverless_service(service_name: str):
    service = services_map.get(service_name)
    if service is None:
        abort(404)
    answer = process_manager.run_function_on_endpoint(service, request.args)
    global request_count
    request_count += 1
    return answer


@app.route('/active_processes', methods=['GET'])
def active_processes():
    return [process.pid for process in process_manager.function_processes]


@app.route('/request_counter', methods=['GET'])
def request_counter():
    return str(request_count)


if __name__ == "__main__":
    scheduler = APScheduler()
    scheduler.add_job(id="close_idle_processes", func=process_manager.close_idle_processes, trigger='interval',
                      seconds=2)
    scheduler.init_app(app)
    scheduler.start()
    app.run()
