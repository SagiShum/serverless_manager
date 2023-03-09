import time


def sleep_and_sum(num1: str, num2: str) -> str:
    """
    :param num1: string of integer
    :param num2: string of integer
    :return: sum of integers
    """
    time.sleep(3)
    return str(int(num1) + int(num2))  # Flask can't return an integer as a response
