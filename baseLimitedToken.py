from baseAccount import CBaseAccount

class CBaseLimitedToken(CBaseAccount):
    def __init__(self, DB, tokenName, totalSupply, address):
        super().__init__(DB, tokenName, address)
        self.totalSupply = totalSupply
