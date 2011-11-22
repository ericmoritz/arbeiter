from clock_job import input_job, print_job
from multiprocessing import Process


if __name__ == '__main__':
    p1 = Process(target=input_job.run)
    p1.start()

    p2 = Process(target=print_job.run)
    p2.start()
    
