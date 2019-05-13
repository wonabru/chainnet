from sqlitedict import SqliteDict

class CDataBase(object):
    def __init__(self):
        try:
            self.close()
        except:
            pass
        self.mydict = SqliteDict('./DB/my_db.sqlite', autocommit=True)
        self.show()

    def set(self, key, value):
        self.mydict[key] = value
            
    def get(self, key):
        if key in self.mydict.keys():
            ret = self.mydict[key]
        else:
            ret = None
        return ret
    
    def show(self, start_with=''):
        for key, value in self.mydict.items():
            if key.find(start_with):
                print(key, '\t',value, '\n')
    
    def clear(self):
        self.mydict.clear()
        
        
    def close(self):
        self.mydict.close()