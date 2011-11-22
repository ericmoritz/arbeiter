from arbeiter import Job, Spout
from datetime import datetime
import time

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


def ticker():
    while True:
        yield "%d" % (time.time(), )
        time.sleep(0.1)

tick_spout = Spout(["127.0.0.1:22133"], "clock-work-queue", ticker())
input_job  = Job(["127.0.0.1:22133"], "clock-work-queue", tick_to_iso8601)
print_job  = Job(["127.0.0.1:22133"], "printer", print_handler)
