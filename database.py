from sqllite import CDataBase as sqllite
from kademliaGetSet import CDataBase

class CSQLLite():
    def __init__(self, ownAddress):
        self.nodes = []
        self.sqllite = sqllite()
        self.kade = CDataBase()

        self.kade.initiate()
        self.kade.runServer()
        self.register_node('127.0.0.1', ownAddress)
        self.bootstrapNodes()


    def save(self, key, value):
        self.sqllite.set(key=str(key), value=value)
        print('SAVE = '+str(value))

        self.kade.set(key=str(key), value=str(value))
        return self.sqllite.get(str(key))

    def get(self, key):

        response_local = self.sqllite.get(key=str(key))
        import ast
        if response_local is None:
            response = self.kade.get(key=str(key))

            if response is not None:
                self.save(key, response)
                response = ast.literal_eval(response.replace('true', 'True').replace('false', 'False'))
            return response
        else:
            return response_local

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
