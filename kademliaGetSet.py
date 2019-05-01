import logging
import asyncio
from kademlia.network import Server
import time

class CDataBase(object):
    def __init__(self):
        self.server = None
        self.loop = None
        self.port = 10023

    def initiate(self):
        if self.server is None:
            self.loop = asyncio.get_event_loop()
            self.server = Server(ksize=100, alpha=10)
            #self.loop.run_until_complete(self.server.listen(self.port+1000))
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            log = logging.getLogger('kademlia')
            log.addHandler(handler)
            log.setLevel(logging.CRITICAL)
            self.loop.set_debug(True)

    def set(self, key, value, count):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.server.set(key, value))
        return self.get(key)

    def get(self, key):
        self.loop = asyncio.get_event_loop()
        return self.loop.run_until_complete(self.server.get(key))

    def bootstrap(self, nodes):
        self.loop = asyncio.get_event_loop()
        bootstrap_node = []
        try:
            for n in nodes:
                bootstrap_node.append((n, self.port))
            self.loop.run_until_complete(self.server.bootstrap(bootstrap_node))
        except:
            pass
