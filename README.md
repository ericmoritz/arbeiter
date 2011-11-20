# Arbeiter

Arbeiter is a really simple worker queue system that using Kestrel as
the messaging system.


## Usage

    from arbeiter import Arbeiter
    
    def handler(a, data):
        return {"output": data}

    job = Arbeiter(["127.0.0.1:22133"], "input", handler)
    job.run()

This is as simple as it gets.  We set up a data handler for the input queue.

All the handler does is stuff the data into the "output" queue.

## handler(a, data)

The handler can do a three things: send data to queues, act as a sink, or fail.


### Send data to queues

If the handler returns a dict or a list of (channel, data) pairs.  Arbeiter
will send that data to those channels.

    def handler(a, data):
        return {"channel-1": data}

    def spit_words(a, data):
        words = data.split(" ")
        return [("words", word) for word in words]

If the data your handler is publishing is time consuming or memory intensive,
you can use a generator to pushlish the data as soon as it is ready:

    def handler(a, key_list):
       key_list = key_list.spilt(",")

       def datagen():
           for key in key_list:
               yield ("data", db.get(key))

       return datagen()


### Act as a sink

If the handler returns a falsey value, it acts as a sink:

    def handler(a, data):
        data = json.loads(data)
        db.store(data['key'], data)


### Fail

If something goes wrong with the sink and it throws an error, the
data will be placed back onto the head of the queue.

    def handler(a, data):
        value = int(data) # This could throw a ValueError

If you want to drop the value because it is invalid, simply return a falsey
value.

    def handler(a, data):
        try:
           value = int(data)
        except ValueError:
           log.exception("someone set us up the bomb")
           return False

        return {"timed-two": str(value * 2)}

## Parellelism

Arbeiter does not assume it knows what is best for your application when it
comes to parellelism.  Some problems are better solved using processes,
others with threads/micro-threads.

The fastest way to add parellelism is to run multiple python processes
of the same job:

    def some_cpu_bound_handler(a, data):
        result = dosomething_cpu_intensive(data)
        return {"out": result}

    job = Arbeiter(["127.0.0.1:22133"], "in", some_cpu_bound_handler)
    
    if __name__ == '__main__':
       job.start()

From bash:

    $ python job.py &
    $ python job.py &
    $ python job.py &


Another way is to use Python's multiprocessing module:

    from job import job
    import multiprocessing as mp

    for i in range(mp.cpu_count()):
        Process(target=job.run).start()

## Worker pool

Because Arbeiter uses Kestrel is its messaging system.  You can easily
run your job on multiple machines as long as they can reach your Kestrel
cluster.

    localhost:~/ $ scp job.py worker1:~/
    localhost:~/ $ scp job.py worker2:~/
    localhost:~/ $ scp job.py worker3:~/

    worker1:~/ $ python job.py &
    worker2:~/ $ python job.py &
    worker3:~/ $ python job.py &

Now from a python prompt, you can push to work into the worker pool:

    localhost:~/ $ python
    >>> from job import job
    >>> fh = open("huge.csv")
    >>> for line in fh:
    ...     job.push(line)
    ...
    >>>

## Conclusion

There you have it, a really simple real time worker queue system.
