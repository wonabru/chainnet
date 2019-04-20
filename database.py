from sqllite import CDataBase

class CSQLLite():
    def __init__(self):
        self.kade = CDataBase()

    def save(self, key, value):
        self.kade.set(key=str(key), value=value)

    def get(self, key):
        return self.kade.get(key=str(key))
    
    def close(self):
        self.kade.close()

