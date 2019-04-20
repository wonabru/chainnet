import numpy as np
from account import CAccount

class CLimitedToken(CAccount):
    def __init__(self, tokenName, totalSupply, creator):
        self.creator = 0
        super().__init__(tokenName, creator)
        self.totalSupply = totalSupply
        if creator == 0:
            self.owner = CAccount()
        self.owner.setAmount(totalSupply)
        
    
