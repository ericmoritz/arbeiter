from kestrel import client as kestrel
import memcache
import random
import types

class KestrelMemcacheClient(kestrel.KestrelMemcacheClient):
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
    

class Client(kestrel.Client):
    def __init__(self, servers, queue):
        self.__memcache = KestrelMemcacheClient(servers=servers)
        self.queue = queue

