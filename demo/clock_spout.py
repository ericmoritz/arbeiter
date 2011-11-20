import time
from clock_worker import input_job

def tick_spout(q):
    while True:
        q.push("%d" % (time.time(), ))
        time.sleep(0.300)
        

if __name__ == '__main__':    
    tick_spout(input_job)
