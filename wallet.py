from Crypto.Signature import PKCS1_v1_5
from Crypto import Hash
from isolated_functions import *
import pyAesCrypt
import io

class CWallet:
	bufferSize = 64 * 1024
	def __init__(self, name_of_wallet = None, from_scratch=False):
		self.password = "strzalwkolano"
		if name_of_wallet is None or name_of_wallet.find('?') >= 0:
			return
		else:
			self.RSAkey = self.checkWalletExist(name_of_wallet, raiseErrorIfNotExist=not from_scratch)
		self.pubKey = self.getPublicKey(self.RSAkey)

	def getPublicKey(self, key):
		pub = encode(key.publickey().n)
		return pub

	def exportDER(self, key):
		return key.exportKey('DER')

	def importFromDER(self, values):
		priv = RSA.importKey(values)
		return priv

	def jsonifyKey(self, key):
		message = {
			'd': key.key.d,
			'q': key.key.q,
			'p': key.key.p,
			'u': key.key.u,
			'n': key.key.n,
			'e': key.key.e
		}
		return message

	def privfromJson(self, values):
		priv = RSA.generate(1024)
		priv.key.d = int(values['d'])
		priv.key.p = int(values['p'])
		priv.key.q = int(values['q'])
		priv.key.n = int(values['n'])
		priv.key.u = int(values['u'])
		priv.key.e = int(values['e'])
		return priv

	def saveWallet(self, priv, name, password, overwrite=False):
		import os
		fCiph = io.BytesIO()
		fin = io.BytesIO(priv)
		if os.path.isfile("./wallets_cipher/" + remove_special_char(name[:20]) + ".wallet.dat") == False or overwrite == True:
			with open("./wallets_cipher/" + remove_special_char(name[:20]) + ".wallet.dat", 'wb') as outfile:
				pyAesCrypt.encryptStream(fin, fCiph, password, self.bufferSize)
				outfile.write(fCiph.getvalue())

	def load_wallet_not_ciphered(self, name):
		try:
			with open("./wallets/" + remove_special_char(name[:20]) + ".wallet.dat", 'rb') as file:
				data = file.read()
		except:
			return None
		return data

	def loadWallet(self, name, password):
		try:
			fdecrypt = io.BytesIO()

			with open("./wallets_cipher/" + remove_special_char(name[:20]) + ".wallet.dat", 'rb') as file:
				data = file.read()
				fin = io.BytesIO(data)
				pyAesCrypt.decryptStream(fin, fdecrypt, password, self.bufferSize, len(fin.getvalue()))
		except:
			return self.load_wallet_not_ciphered(name)
		return fdecrypt.getvalue()

	def redefineRSAkey(self, key):
		values = self.jsonifyKey(key)
		return self.privfromJson(values)

	def checkWalletExist(self, name_of_wallet, raiseErrorIfNotExist = True):
		self.RSAkey = self.loadWallet(name_of_wallet, self.password)
		if raiseErrorIfNotExist and self.RSAkey is None:
			print('Wallet file ' + name_of_wallet + '.wallet.dat not found !!')
			return None
		if self.RSAkey is None:
			self.RSAkey = RSA.generate(1024)
			self.saveWallet(self.exportDER(self.RSAkey), self.getPublicKey(self.RSAkey), self.password)
		else:
			self.RSAkey = self.importFromDER(self.RSAkey)
			self.saveWallet(self.exportDER(self.RSAkey), self.getPublicKey(self.RSAkey), self.password)

		return self.RSAkey



	def sign(self, message):
		signer = PKCS1_v1_5.new(self.RSAkey)
		digest = Hash.SHA256.new()
		digest.update(serialize(message))
		sgn = signer.sign(digest)
		return b64encode(sgn).decode('utf-8')

	@staticmethod
	def verify(message, signature, pub_keyencode):
		rsa_temp.key.key.n = decode(pub_keyencode)
		signer = PKCS1_v1_5.new(rsa_temp.key.publickey())
		digest = Hash.SHA256.new()
		digest.update(serialize(message))
		return signer.verify(digest, b64decode(signature.encode('utf-8')))

	@staticmethod
	def check_address(address):
		if address == '':
			return False

		return True