from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Hash
from base64 import b64decode,b64encode
import pickle

class CWallet:
	def __init__(self, name_of_wallet = None):
		if name_of_wallet is None:
			return
		else:
			self.RSAkey = self.checkWalletExist(name_of_wallet)
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
		with open("./wallets/" + name + ".wallet.dat", 'wb') as outfile:
			outfile.write(priv)

	def loadWallet(self, name):
		try:
			with open("./wallets/" + name + ".wallet.dat", 'rb') as file:
				data = file.read()
		except:
			return None
		return data

	def redefineRSAkey(self, key):
		values = self.jsonifyKey(key)
		return self.privfromJson(values)

	def checkWalletExist(self, name_of_wallet, raiseErrorIfNotExist = False):
		self.RSAkey = self.loadWallet(name_of_wallet)
		if raiseErrorIfNotExist and self.RSAkey is None: raise 'Wallet file "' + name_of_wallet + '.wallet.dat" not found !!'
		if self.RSAkey is None:
			self.RSAkey = RSA.generate(1024)
			self.saveWallet(self.exportDER(self.RSAkey), name_of_wallet)
		else:
			self.RSAkey = self.importFromDER(self.RSAkey)

		return self.RSAkey

	def serialize(self, message):
		return pickle.dumps(message)

	def unserialize(self, ser_message):
		return pickle.loads(ser_message)

	def sign(self, message, priv_key):
		signer = PKCS1_v1_5.new(priv_key)
		digest = Hash.SHA256.new()
		digest.update(self.serialize(message))

		sgn = signer.sign(digest)
		return b64encode(sgn).decode('utf-8')

	def verify(self, message, signature, pub_keyencode):
		self.RSAkey._n = self.decode(pub_keyencode)
		signer = PKCS1_v1_5.new(self.RSAkey.publickey())
		digest = Hash.SHA256.new()
		digest.update(self.serialize(message))
		return signer.verify(digest, b64decode(signature.encode('utf-8')))

	@staticmethod
	def check_address(address):
		if address == '':
			return False

		return True