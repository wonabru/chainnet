from sqllite import CDataBase as sqllite
from kademliaGetSet import CDataBase

instance_kade = None

class CSQLLite():
    def __init__(self, ownAddress):

        global instance_kade
        if instance_kade is None:
            self.nodes = []
            self.sqllite = sqllite()
            self.kade = CDataBase()

            self.kade.initiate()
            self.kade.runServer()
            self.register_node('127.0.0.1', ownAddress)
            self.bootstrapNodes()
            instance_kade = self
        else:
            self.nodes = instance_kade.nodes
            self.sqllite = instance_kade.sqllite
            self.kade = instance_kade.kade


    def save(self, key, value, announce=''):
        if isinstance(key, str) == False: key = str(key)
        self.sqllite.set(key=announce+key, value=value)
        if announce != '':
            self.announce(announce+key, value)
        return self.sqllite.get(announce+key)

    def get(self, key):
        if isinstance(key, str) == False: key = str(key)
        self.sqllite.show('Lock:')
        return self.sqllite.get(key=key)

    def announce(self, key, value):
        self.kade.set(key=key, value=str(value))

    def look_at(self, key):
        import ast
        if isinstance(key, str) == False: key = str(key)
        response = self.kade.get(key=key)

        if response is not None:
            #self.save(key, response)
            response = ast.literal_eval(response.replace('true', 'True').replace('false', 'False'))
        return response

    def close(self):
        self.sqllite.close()

    def register_node(self, address, publicKey):
        if (address, publicKey) not in self.nodes:
            self.nodes.append((address, publicKey))

    def bootstrapNodes(self):
        nodes = []
        for n in self.nodes:
            if n[0] not in nodes:
                nodes.append(n[0])

        self.kade.bootstrap(nodes=nodes, port=5002)
