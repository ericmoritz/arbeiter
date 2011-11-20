import memcache

class Arbeiter(object):

    def __init__(self, servers, input_queue, handler, default_timeout=100):
        self.servers = servers
        self.input_queue = input_queue
        self.handler = handler
        self.client = memcache.Client(servers)
        self.default_timeout = default_timeout

    def flush(self, queue=None):
        queue = queue or self.input_queue

        for s in self.client.servers:
            if not s.connect(): continue
            s.send_cmd("FLUSH %s" % (self.input_queue, ))
            s.expect("OK")
        
    def push(self, data, queue=None):
        queue = queue or self.input_queue

        self.client.set(queue, data)

    def get(self, queue, timeout=None, durable=False):
        if timeout is not None:
            queue += "/t=%d" % (timeout, )

        if durable:
            queue += "/open"

        return self.client.get(queue)

    def consume(self, queue=None):
        queue = queue or self.input_queue
        self.client.get(queue + "/close")
        
    def handle_one(self, timeout=None):
        timeout = timeout or self.default_timeout

        data = self.get(self.input_queue, timeout=timeout, durable=True)

        if data: 
            result = self.handler(self, data)
            if result:
                for queue, value in result.items():
                    self.push(value, queue=queue)

            # Nothing bad happend, consume the data
            self.consume()
    
    def run(self):
        while True:
            self.handle_one()
