from sqlitedict import SqliteDict

class CDataBase(object):
    def __init__(self):
        try:
            self.close()
        except:
            pass
        self.mydict = SqliteDict('./my_db.sqlite', autocommit=True)
        self.clear()
        self.show()

    def set(self, key, value):
        self.mydict[key] = value
            
    def get(self, key):
        ret = self.mydict[key]
        return ret
    
    def show(self):
        for key, value in self.mydict.items():
            print(key, value)
    
    def clear(self):
        self.mydict.clear()
        
        
    def close(self):
        self.mydict.close()