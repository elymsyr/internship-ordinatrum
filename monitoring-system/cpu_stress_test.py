import time
from datetime import datetime, timedelta

def cpu_intensive_task(duration_seconds):
    end_time = datetime.now() + timedelta(seconds=duration_seconds)
    while datetime.now() < end_time:
        result = 0
        for i in range(1000000):
            result += i

if __name__ == "__main__":
    print("Starting CPU-intensive task...")
    start_time = time.time()
    cpu_intensive_task(30)
    end_time = time.time()
    print(f"Task completed in {end_time - start_time} seconds.")