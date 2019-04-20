import numpy as np
from baseAccount import CBaseAccount

class CBaseLimitedToken(CBaseAccount):
    def __init__(self, tokenName, totalSupply):
        super().__init__(tokenName)
        self.totalSupply = totalSupply