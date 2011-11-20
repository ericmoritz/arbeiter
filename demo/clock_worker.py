from arbeiter import Arbeiter
from multiprocessing import Process
from datetime import datetime


def tick_to_iso8601(a, data):
    # Convert tick string to seconds
    seconds = float(data)

    if seconds % 2 == 0:
        return # Supress all even seconds 

    # Convert seconds to a datetime object
    dt = datetime.fromtimestamp(seconds)

    return {"printer": dt.isoformat()}

    
def print_handler(a, data):
    print data

    
input_job = Arbeiter(["127.0.0.1:22133"], "clock-work-queue", tick_to_iso8601)
print_job = Arbeiter(["127.0.0.1:22133"], "printer", print_handler)


if __name__ == '__main__':
    p1 = Process(target=input_job.run)
    p1.start()

    p2 = Process(target=print_job.run)
    p2.start()
    
