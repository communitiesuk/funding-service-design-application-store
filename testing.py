import threading
import time
from concurrent.futures import ThreadPoolExecutor


def print_data():
    current_thread = threading.current_thread()
    thread_id = f"[{current_thread.name}:{current_thread.ident}]"
    for x in range(6):
        time.sleep(2)
        print(thread_id + " " + str(x))


executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="TestingExecutor")
for x in range(4):
    executor.submit(print_data)

print_data()
