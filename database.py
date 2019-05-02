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
            from node import run_kademlia_node

            run_kademlia_node(self.kade.port, self.kade.server, self.kade.loop)
            instance_kade = self
        else:
            self.nodes = instance_kade.nodes
            self.sqllite = instance_kade.sqllite
            self.kade = instance_kade.kade


    def save(self, key, value, announce=''):
        if isinstance(key, str) == False:
            key = str(key)
        if announce == 'DO NOT SAVE LOCAL':
            _current = self.sqllite.get(announce)
            if _current is None:
                self.sqllite.set(key=announce, value=[key, ])
            else:
                _current.append(key)
                self.sqllite.set(key=announce, value=_current)

        else:
            _not_save_local = self.sqllite.get('DO NOT SAVE LOCAL')

            if _not_save_local is None: _not_save_local = []

            if not (key in _not_save_local and announce == 'Account:'):
                self.sqllite.set(key=announce + key, value=value)

                if announce != '':
                    self.announce(announce + key, value)
        return self.sqllite.get(announce + key)

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
