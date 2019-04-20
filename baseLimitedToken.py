from baseAccount import CBaseAccount

class CBaseLimitedToken(CBaseAccount):
    def __init__(self, DB, tokenName, totalSupply):
        super().__init__(DB, tokenName)
        self.totalSupply = totalSupply
