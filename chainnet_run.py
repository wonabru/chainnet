import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from init_chainnet import CInitChainnet
from wallet import CWallet
from actionToken import CActionToken
from limitedToken import CLimitedToken
from account import CAccount
import ast

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.chainnet = CInitChainnet()
		self.my_main_wallet = self.chainnet.wallet
		self.my_main_account = self.chainnet.my_account
		self.my_accounts = {}
		self.update_my_accounts()
		self.master = master
		self.pack()
		self.create_tabs()
		self.create_account_tab()
		self.create_create_tab()
		self.create_send_tab()


	def update_my_accounts(self):
		self.init_account = self.chainnet.Qcoin.initAccount
		_my_accounts = self.my_main_account.kade.get('my_main_accounts')
		if _my_accounts is None:
			_my_accounts = [self.my_main_account.address]
		else:
			_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))
		for acc in _my_accounts:
			_account = CAccount(self.my_main_account.kade, '__temp__', None, acc)
			try:
				_account.update()
				_wallet = CWallet(_account.accountName)
				if _account.address != self.init_account.address:
					self.my_accounts[_account.address] = {'account': _account, 'wallet': _wallet}
			except Exception as ex:
				messagebox.showerror(title='Error loading file', message=str(ex))

	def create_tabs(self):
		self.tab_control = ttk.Notebook(self.master)
		self.account_tab = ttk.Frame(self.tab_control)
		self.create_tab = ttk.Frame(self.tab_control)
		self.send_tab = ttk.Frame(self.tab_control)
		self.receive_tab = ttk.Frame(self.tab_control)
		self.tab_control.add(self.account_tab, text='Accounts balances')
		self.tab_control.add(self.create_tab, text='Create Account')
		self.tab_control.add(self.send_tab, text='Send')
		self.tab_control.add(self.receive_tab, text='Receive')
		self.tab_control.pack(expand=1, fill='both')

	def create_account_tab(self):
		self.amounts = {}
		self.accounts_balances = {}
		for add, acc in self.my_accounts.items():
			self.add_new_account(add, acc['account'])

	def add_new_account(self, address, account):
		self.accounts_balances[address] = {}
		self.amounts[address] = {}
		self.add_new_amounts(address, account)
		self.my_main_account.kade.save('my_main_accounts', str(list(self.my_accounts.keys())))
		self.update_amounts(address)


	def add_new_amounts(self, address, account):
		for key, token in account.amount.items():
			if key not in self.amounts[address]:
				self.amounts[address][key] = tk.StringVar()
				self.accounts_balances[address][key] = tk.Label(self.account_tab, textvariable=self.amounts[address][key],
				                                            font=("Helvetica", 16)).pack()

	def create_send_tab(self):
		tk.Label(self.send_tab, text='Choose token name:',
								font=("Helvetica", 16)).pack()
		self.tokens_cmb = ttk.Combobox(self.send_tab)
		self.tokens_cmb['values'] = [str(token.accountName) for key, token in self.chainnet.tokens.items()]
		self.tokens_cmb.pack()
		tk.Label(self.send_tab, text='From account by name:',
								font=("Helvetica", 16)).pack()
		self.my_accounts_cmb = ttk.Combobox(self.send_tab)
		self.my_accounts_cmb['values'] = [acc['account'].accountName+' '+
		                                  ''.join(str(value)+' '+str(self.chainnet.get_token(key).accountName)
		                                           for key, value in acc['account'].amount.items())
		                                  for acc in self.my_accounts.values()]
		self.my_accounts_cmb.pack()
		tk.Label(self.send_tab, text='To account by name:',
								font=("Helvetica", 16)).pack()
		self.send_address_ent = tk.Entry(self.send_tab, width=30, font=("Helvetica", 16))
		self.send_address_ent.pack()
		_amount = tk.DoubleVar()
		_amount.set(0.01)
		self.amount_spin = tk.Spinbox(self.send_tab, from_=0, to=100000000000, width=20, textvariable=_amount)
		self.amount_spin.pack()
		tk.Button(self.send_tab, text="Send",
									command=lambda: self.send_coins(self.my_accounts_cmb.get(),
																	self.send_address_ent.get(),
									                                self.amount_spin.get(),
									                                self.tokens_cmb.get())).pack()
		tk.Button(self.send_tab, text="Attach",
									command=lambda: self.attach(self.send_address_ent.get(),
																self.my_accounts_cmb.get(),
									                                self.tokens_cmb.get())).pack()

	def attach(self, account, attacher, token):
		try:
			account = self.select_my_acount_by_name(account)
			attacher = self.select_my_acount_by_name(attacher)
			token = self.chainnet.get_token_by_name(token)
			if attacher.address in token.chain.uniqueAccounts:
				if token.attach(account, attacher=attacher):
					self.add_new_amounts(account.address, account=account)
					self.update_amounts(account.address)
					self.update_amounts(attacher.address)
					messagebox.showinfo(title='Attach with success', message=account.accountName + ' now can pay with ' +
					                                                       token.accountName)
					return
				else:
					messagebox.showerror(title='Attach', message=account.accountName + ' could not be attach to ' +
					                                                       token.accountName +
					                                             '. Suppose ' + attacher.accountName +
					                                             ' not in a connection with ' + account.accountName)
			else:
				messagebox.showerror(title='Attach', message=attacher.accountName + ' is not connected to ' +
				                                                       token.accountName)
		except Exception as ex:
			messagebox.showerror(title='Could not attach', message=str(ex))

	def send_coins(self, from_account, to_account, amount, token):
		try:
			amount = float(amount)

			from_account = self.select_my_acount_by_name(from_account)
			to_account = self.select_my_acount_by_name(to_account)#self.my_main_account.chain.uniqueAccounts[to_account]
			token = self.chainnet.get_token_by_name(token)
			if to_account.address in token.chain.uniqueAccounts and from_account.address in token.chain.uniqueAccounts:
				if from_account.send(to_account, token, amount):
					self.update_amounts(from_account.address)
					self.update_amounts(to_account.address)
					messagebox.showinfo(title='Send with success', message=from_account.accountName+' sent '+
					                                                       str(amount)+' of '+token.accountName+' to token '+
					                    to_account.accountName)
					return
				else:
					messagebox.showerror(title='Send', message='Not enough funds on '+from_account.accountName)
			else:
				messagebox.showerror(title='Send', message='You need first attach '+to_account.accountName+' to '+token.accountName)
		except:
			messagebox.showerror(title='Send', message='Coins not send')



	def create_create_tab(self):
		self.selected_account = tk.IntVar()
		self.selected_account.set(1)
		rad1 = tk.Radiobutton(self.create_tab, text='Create new simple account from scratch', value=1,
		                      variable=self.selected_account)
		rad2 = tk.Radiobutton(self.create_tab, text='Create new simple account using public address',
					   value=2, variable=self.selected_account)
		rad3 = tk.Radiobutton(self.create_tab, text='Create new Limited Token',
					   value=3, variable=self.selected_account)
		rad4 = tk.Radiobutton(self.create_tab, text='Create new Action Token',
					   value=4, variable=self.selected_account)
		rad1.pack()
		rad2.pack()
		rad3.pack()
		rad4.pack()
		tk.Label(self.create_tab, text='Set new account name:',
								font=("Helvetica", 16)).pack()
		self.new_name_ent = tk.Entry(self.create_tab, width=30, font=("Helvetica", 16))
		self.new_name_ent.pack()
		tk.Label(self.create_tab, text='Set new address:',
								font=("Helvetica", 16)).pack()
		self.new_address_ent = tk.Entry(self.create_tab, width=50, font=("Helvetica", 16))
		self.new_address_ent.pack()
		tk.Label(self.create_tab, text='Set total/initial supply:',
		         font=("Helvetica", 16)).pack()
		_amount = tk.DoubleVar()
		_amount.set(0.01)
		self.supply_spin = tk.Spinbox(self.create_tab, from_=1, to=1000000000000, width=20, textvariable=_amount)
		self.supply_spin.pack()
		tk.Button(self.create_tab, text="Create new account",
									command=lambda: self.create_new_account(self.new_name_ent.get(),
																			self.new_address_ent.get(),
									                                        self.supply_spin.get())).pack()

	def create_new_account(self, accountName, address, initSupply):
		if accountName == '':
			messagebox.showwarning(title='Account name', message='Account name cannot be empty')
			return
		if self.selected_account.get() == 2 and CWallet().check_address(address) == False:
			messagebox.showwarning(title='Account address', message='Proper account address must be set')
			return

		initSupply = float(initSupply)
		if self.selected_account.get() == 1:
			_wallet = CWallet(accountName)

			_account = self.chainnet.baseToken.create(accountName=accountName, creator=self.my_main_account, address=_wallet.pubKey)
			if _account is None:
				messagebox.showerror(title='Error in account creating', message='Account is not created')
				return
			self.new_address_ent.delete(0, tk.END)
			self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
			self.new_address_ent.pack()
			self.my_accounts[_account.address] = {'account': _account, 'wallet': _wallet}
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.add_new_account(_account.address, account=_account)
			self.update_amounts(_account.address)
			messagebox.showinfo('Account created', _account.accountName + ' from now you are in Chainnet')

		if self.selected_account.get() == 2:
			_account = self.chainnet.baseToken.create(accountName=accountName, creator=self.my_main_account, address=address)
			messagebox.showinfo('Account created', _account.accountName + ' from now you are in Chainnet')

		if self.selected_account.get() == 3:
			_wallet = CWallet(accountName)
			_limitedToken = CLimitedToken(self.chainnet.DB, accountName, initSupply, creator=self.my_main_account, address=_wallet.pubKey)
			if _limitedToken is None:
				messagebox.showerror(title='Error in token creating', message='Token is not created')
				return
			self.new_address_ent.delete(0, tk.END)
			self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
			self.new_address_ent.pack()
			self.my_accounts[_limitedToken.address] = {'account': _limitedToken, 'wallet': _wallet}
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.chainnet.add_token(_limitedToken)
			self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.add_new_account(_limitedToken.address, account=_limitedToken)
			self.add_new_amounts(self.my_main_account.address, account=_limitedToken)
			self.add_new_amounts(_limitedToken.address, account=_limitedToken)
			self.update_amounts(self.my_main_account.address)
			self.update_amounts(_limitedToken.address)
			messagebox.showinfo('Limited Token is created', _limitedToken.accountName + ' is now created with total supply: '+str(_limitedToken.totalSupply))

		if self.selected_account.get() == 4:
			_wallet = CWallet(accountName)
			_actionToken = CActionToken(self.chainnet.DB, accountName, initSupply, creator=self.my_main_account, address=_wallet.pubKey)
			if _actionToken is None:
				messagebox.showerror(title='Error in token creating', message='Token is not created')
				return
			self.new_address_ent.delete(0, tk.END)
			self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
			self.new_address_ent.pack()
			self.my_accounts[_actionToken.address] = {'account': _actionToken, 'wallet': _wallet}
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.chainnet.add_token(_actionToken)
			self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.add_new_account(_actionToken.address, account=_actionToken)
			self.add_new_amounts(self.my_main_account.address, account=_actionToken)
			self.add_new_amounts(_actionToken.address, account=_actionToken)
			self.update_amounts(self.my_main_account.address)
			self.update_amounts(_actionToken.address)
			messagebox.showinfo('Action Token is created',
			                    _actionToken.accountName + ' is now created with initial supply: ' + str(
				                    _actionToken.totalSupply))

	def select_my_acount_by_name(self, name):

		for add, acc in self.my_accounts.items():
			if acc['account'].accountName == name.split(' ')[0]:
				return acc['account']
		return None

	def update_amounts(self, address):
		self.update_my_accounts()
		_account = self.my_accounts[address]['account']
		for key, amount in _account.amount.items():
			token_name = self.chainnet.tokens[key].accountName
			self.amounts[address][key].set(_account.accountName + ': ' + str(amount) + '  ' + token_name)

root = tk.Tk()
root.title("Chainnet Wallet App")

app = Application(master=root)
root.geometry('600x400')
app.mainloop()