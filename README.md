# Arbeiter

Arbeiter is an unassuming worker queue system that uses Kestrel as the
messaging queue.

Arbeiter acts as a middleman, it takes an item off an input queue, lets you
process it and then forwards it on to zero, one or many outgoing queues.

Arbeiter is unassuming in the fact that it does not assume to know
what is best for your application in terms of data serialization,
error handling or parellelism.

## Usage

    from arbeiter import Arbeiter
    
    def handler(a, data):
        return {"output": data}

    job = Arbeiter(["127.0.0.1:22133"], "input", handler)
    job.run()

This listens for items being pushed into the "input" queue and then forwards
them to the queue named "output".

To publish a message:

    job.push("Hello, World!")

Arbeiter does not assume it knows what format is best for you, so it only 
uses bytes.

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
you can use a generator to publish the data as soon as it is ready:

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

If something goes wrong with the handler and it throws an error, the
data will be placed back onto the head of the queue.

    def handler(a, data):
        value = int(data) # This could throw a ValueError

Because the item is placed back on the head of the queue, an error
like above will cause a chain reaction that causes all the workers to
crash as they try to process that faulty item.  That'll teach you to
write error handling code, ay?

If you want to drop the value because it is invalid, simply return a
falsey value and Arbeiter will tell Kestrel to close the item.

    def handler(a, data):
        try:
           value = int(data)
        except ValueError:
           log.exception("someone set us up the bomb")
           return False

        return {"times-two": str(value * 2)}

You could also stuff the value into a special queue if you wanted to 
write a fix for the error:

    def handler(a, data):
        try:
           value = int(data)
        except ValueError:
           log.exception("someone set us up the bomb")           
           return {"times-two-failures": data}

        return {"times-two": str(value * 2)}


On the topic of failures; Arbeiter does not assume it knows what you
want when handling errors.  When bad things happens, Arbeiter lets the
exception raise.

This means that if you do not handle your exceptions, your worker
process will die a painful death.  This may be what you want or it may
not; but you should know that Arbeiter treats you like an adult.

Hint: you may want to do something like this to keep things running:

    while True:
        try:
            job = Arbeiter(["127.0.0.1:22133"], "in", myhandler)
            job.run()
        except:
            log.exception("Well, damn, let's try that again.")
    

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

Because Arbeiter uses Kestrel as its messaging system.  You can easily
run your job on multiple machines as long as they can reach your Kestrel
cluster.

    localhost:~/ $ scp job.py worker1:~/
    localhost:~/ $ scp job.py worker2:~/
    localhost:~/ $ scp job.py worker3:~/

    worker1:~/ $ python job.py &
    worker2:~/ $ python job.py &
    worker3:~/ $ python job.py &

Now from a python prompt, you can push work into the worker pool:

    localhost:~/ $ python
    >>> from job import job
    >>> fh = open("huge.csv")
    >>> for line in fh:
    ...     job.push(line)
    ...
    >>>

## Conclusion

There you have it, a really simple real time worker queue system.
