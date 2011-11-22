from kestrel import client as kestrel
import memcache
import types
import random


class RetryLimitExceeded(Exception):
    pass


class Client(kestrel.KestrelMemcacheClient):
    def _get_server(self, key):
        if type(key) == types.TupleType:
            serverhash, key = key
        else:
            serverhash = random.randint(0, len(self.buckets))

        for i in range(memcache.Client._SERVER_RETRIES):
            server = self.buckets[serverhash % len(self.buckets)]
            if server.connect():
                #print "(using server %s)" % server,
                return server, key
            serverhash = random.randint(0, len(self.buckets))
        return None, None
    


class Job(object):

    def __init__(self, servers, input_queue, handler,
                 default_timeout=1000,
                 retry_limit=3):

        self.servers = servers
        self.input_queue = input_queue
        self.handler = handler
        self.client = Client(servers)
        self.default_timeout = default_timeout
        self.retry_limit = retry_limit

    def flush(self, queue=None):
        queue = queue or self.input_queue

        for s in self.client.servers:
            if not s.connect(): continue
            s.send_cmd("FLUSH %s" % (self.input_queue, ))
            s.expect("OK")
        
    def push(self, data, queue=None):
        queue       = queue or self.input_queue
        retry_limit = self.retry_limit
        client      = self.client

        for i in range(retry_limit):
            result = client.set(queue, data)
        
            if result:
                return result

        raise RetryLimitExceeded()

    def get(self, queue, timeout=None, durable=False):
        if timeout is not None:
            queue += "/t=%d" % (timeout, )

        if durable:
            queue += "/open"

        return self.client.get(queue)

    def peek(self, queue, timeout=None):
        queue += "/peek"

        if timeout is not None:
            queue += "/t=%d" % (timeout, )

        return self.client.get(queue)


    def consume(self, queue=None):
        queue = queue or self.input_queue
        self.client.get(queue + "/close")
        
    def abort(self, queue=None):
        queue = queue or self.input_queue
        self.client.get(queue + "/abort")

    def handle_one(self, timeout=None):
        timeout = timeout or self.default_timeout

        data = self.get(self.input_queue, timeout=timeout, durable=True)

        if data: 
            try:
                result = self.handler(self, data)
                if result:
                    for queue, value in result.items():
                        self.push(value, queue=queue)
            except:
                self.abort()
                raise

            # Nothing bad happend, consume the data
            self.consume()
    
    def run(self):
        while True:
            self.handle_one()


class Spout(object):
    def __init__(self, servers, queue, generator, retry_limit=3):
        self.servers     = servers
        self.queue       = queue
        self.client      = Client(servers)
        self.generator   = generator
        self.retry_limit = retry_limit

    def run(self):
        queue       = self.queue
        client      = self.client
        retry_limit = self.retry_limit

        for data in self.generator:
            result = False

            for i in range(retry_limit):
                result = client.set(queue, data)
                
                if result:
                    break

            if not result:
                raise RetryLimitExceeded()
            

