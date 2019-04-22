import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from init_chainnet import CInitChainnet
from wallet import CWallet
from actionToken import CActionToken
from limitedToken import CLimitedToken

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.chainnet = CInitChainnet()
		self.my_main_wallet = self.chainnet.wallet
		self.my_main_account = self.chainnet.my_account
		self.my_accounts = {}
		self.my_accounts[self.my_main_account.address] = {'account': self.my_main_account, 'wallet': self.my_main_wallet}
		self.master = master
		self.pack()
		self.create_tabs()
		self.create_account_tab()
		self.create_create_tab()
		self.create_send_tab()


	def create_tabs(self):
		self.tab_control = ttk.Notebook(self.master)
		self.account_tab = ttk.Frame(self.tab_control)
		self.create_tab = ttk.Frame(self.tab_control)
		self.send_tab = ttk.Frame(self.tab_control)
		self.receive_tab = ttk.Frame(self.tab_control)
		self.tab_control.add(self.account_tab, text='Account')
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
		tk.Label(self.account_tab, text='Account name: ' + account.accountName,
		         font=("Helvetica", 16)).pack()
		tk.Label(self.account_tab, text='Balances:', font=("Helvetica", 16)).pack()
		self.accounts_balances[address] = {}
		self.amounts[address] = {}
		self.add_new_amounts(address, account)
		self.update_amounts(address)

	def add_new_amounts(self, address, account):
		for key, token in account.amount.items():
			if key not in self.amounts[address]:
				self.amounts[address][key] = tk.DoubleVar()
				self.accounts_balances[address][key] = tk.Label(self.account_tab, textvariable=self.amounts[address][key],
				                                            font=("Helvetica", 16)).pack()

	def create_send_tab(self):
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
		self.amount_spin = tk.Spinbox(self.send_tab, from_=0, to=100000000000, width=5, textvariable=_amount)
		self.amount_spin.pack()
		tk.Button(self.send_tab, text="Send",
									command=lambda: self.send_coins(self.my_accounts_cmb.get(),
																	self.send_address_ent.get(),
									                                self.amount_spin.get(),
									                                self.tokens_cmb.get())).pack()
	def send_coins(self, from_account, to_account, amount, token):
		try:
			amount = float(amount)
			from_account = self.select_my_acount_by_name(from_account)
			to_account = self.select_my_acount_by_name(to_account)#self.my_main_account.chain.uniqueAccounts[to_account]
			token = self.chainnet.get_token_by_name(token)
			if from_account.send(to_account, token, amount):
				self.update_amounts(from_account.address)
				self.update_amounts(to_account.address)
				messagebox.showinfo(title='Send with success', message=from_account.accountName+' sent '+
				                                                       str(amount)+' of '+token.accountName+' to '+
				                    to_account.accountName)
			else:
				messagebox.showerror(title='Send', message='Not enough funds on '+from_account.accountName)
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
		tk.Button(self.create_tab, text="Create new account",
									command=lambda: self.create_new_account(self.new_name_ent.get(),
																			self.new_address_ent.get())).pack()

	def create_new_account(self, accountName, address, initSupply=1):
		if accountName == '':
			messagebox.showwarning(title='Account name', message='Account name cannot be empty')
			return
		if self.selected_account.get() == 2 and CWallet().check_address(address) == False:
			messagebox.showwarning(title='Account address', message='Proper account address must be set')
			return

		if self.selected_account.get() == 1:
			_wallet = CWallet(True)

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
			_wallet = CWallet(True)
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
			self.add_new_amounts(self.my_main_account.address, account=self.my_main_account)
			self.update_amounts(self.my_main_account.address)
			messagebox.showinfo('Limited Token is created', _limitedToken.accountName + ' is now created with total supply: '+str(_limitedToken.totalSupply))

		if self.selected_account.get() == 4:
			_wallet = CWallet(True)
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
			self.add_new_amounts(self.my_main_account.address, account=self.my_main_account)
			self.update_amounts(self.my_main_account.address)
			messagebox.showinfo('Action Token is created',
			                    _actionToken.accountName + ' is now created with initial supply: ' + str(
				                    _actionToken.totalSupply))

	def select_my_acount_by_name(self, name):

		for add, acc in self.my_accounts.items():
			if acc['account'].accountName == name:
				return acc['account']
		return None

	def update_amounts(self, address):
		for key, token in self.my_accounts[address]['account'].amount.items():
			token_name = self.chainnet.tokens[key].accountName
			self.amounts[address][key].set(str(token) + '  ' + token_name)

root = tk.Tk()
root.title("Chainnet Wallet App")

app = Application(master=root)
root.geometry('600x400')
app.mainloop()