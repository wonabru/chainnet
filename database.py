from sqllite import CDataBase as sqllite
from kademliaGetSet import CDataBase
import socket

instance_kade = None


class CSQLLite():
    def __init__(self, ownAddress):

        global instance_kade
        if instance_kade is None:
            node_identifier = socket.gethostbyname(socket.gethostname())
            self.nodes = []
            self.sqllite = sqllite()

            self.kade = CDataBase()
            self.kade.initiate()
            self.register_node(node_identifier)
            self.register_node('127.0.0.1')
            self.bootstrapNodes()
            instance_kade = self
        else:
            self.nodes = instance_kade.nodes
            self.sqllite = instance_kade.sqllite
            self.kade = instance_kade.kade


    def save(self, key, value, announce=''):
        if isinstance(key, str) == False: key = str(key)
        self.sqllite.set(key=key, value=value)
        if announce != '':
            self.announce(announce+key, value)
        return self.sqllite.get(announce+key)

    def get(self, key):
        if isinstance(key, str) == False: key = str(key)
        return self.sqllite.get(key=key)

    def announce(self, key, value):
        print('KADEMLIA SET: ',key,' = ',self.kade.set(key=key, value=str(value)))

    def look_at(self, key):
        import ast
        if isinstance(key, str) == False: key = str(key)
        response = self.kade.get(key=key)

        if response is not None:
            #self.save(key, response)
            try:
                response = ast.literal_eval(response.replace('true', 'True').replace('false', 'False'))
            except:
                pass
        return response

    def close(self):
        self.sqllite.close()

    def register_node(self, address):
        if address not in self.nodes:
            self.nodes.append(address)

    def bootstrapNodes(self):
        self.kade.bootstrap(self.nodes)
