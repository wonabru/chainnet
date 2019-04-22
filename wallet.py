from Crypto.PublicKey import RSA
from base64 import b64decode,b64encode

class CWallet:
	def __init__(self, create_new = None):
		if create_new is None:
			return
		if create_new:
			self.RSAkey = RSA.generate(1024)
			self.saveWallet(self.exportDER(self.RSAkey), "chainnet_wallet")
		else:
			self.RSAkey = self.checkWalletExist()
		self.pubKey = self.getPublicKey(self.RSAkey)

	def encode(self, n):
		b = bytearray()
		while n:
			b.append(n & 0xFF)
			n >>= 8
		return b64encode(b).decode('utf-8')

	def decode(self, s):
		b = bytearray(b64decode(s.encode('utf-8')))  # in case you're passing in a bytes/str
		return sum((1 << (bi * 8)) * bb for (bi, bb) in enumerate(b))

	def getPublicKey(self, key):
		pub = self.encode(key.publickey().n)
		return pub

	def exportDER(self, key):
		return key.exportKey('DER')

	def importFromDER(self, values):
		priv = RSA.importKey(values)
		return priv

	def jsonifyKey(self, key):
		message = {
			'd': key.d,
			'q': key.q,
			'p': key.p,
			'u': key.u,
			'n': key.n,
			'e': key.e
		}
		return message

	def privfromJson(self, values):
		priv = RSA.generate(1024)
		priv._d = int(values['d'])
		priv._p = int(values['p'])
		priv._q = int(values['q'])
		priv._n = int(values['n'])
		priv._u = int(values['u'])
		priv._e = int(values['e'])
		return priv

	def saveWallet(self, priv, name):
		with open(name + ".dat", 'wb') as outfile:
			outfile.write(priv)

	def loadWallet(self, name):
		try:
			with open(name + ".dat", 'rb') as file:
				data = file.read()
		except:
			return None
		return data

	def redefineRSAkey(self, key):
		values = self.jsonifyKey(key)
		return self.privfromJson(values)

	def checkWalletExist(self):
		self.RSAkey = self.loadWallet("chainnet_wallet")
		if self.RSAkey is None:
			self.RSAkey = RSA.generate(1024)
			self.saveWallet(self.exportDER(self.RSAkey), "chainnet_wallet")
		else:
			self.RSAkey = self.importFromDER(self.RSAkey)

		return self.RSAkey

	@staticmethod
	def check_address(address):
		if address == '':
			return False

		return True