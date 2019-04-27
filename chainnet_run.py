import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from init_chainnet import CInitChainnet
from wallet import CWallet
from actionToken import CActionToken
from limitedToken import CLimitedToken
from account import CAccount
import ast
from tkinter import scrolledtext

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.chainnet = CInitChainnet()
		self.my_main_wallet = self.chainnet.wallet
		self.my_main_account = self.chainnet.my_account
		self.my_accounts = {}
		self.column_nr = {}
		self.update_my_accounts()
		self.master = master
		self.create_tabs()
		self.create_account_tab()
		self.create_create_tab()
		self.create_send_tab()
		self.create_info_tab()
		self.pack()

	def update_my_accounts(self):
		try:
			self.init_account = self.chainnet.Qcoin.initAccount
			_my_accounts = self.my_main_account.kade.get('my_main_accounts')
			if _my_accounts is None:
				_my_accounts = [self.my_main_account.address]
			else:
				_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))
			for acc in _my_accounts:
				if acc not in [self.chainnet.init_account.address, ]:
					_account = CAccount(self.my_main_account.kade, '__tempRun__', None, acc)
					try:
						_account.update(with_chain=True)
						_wallet = CWallet(_account.accountName)

						self.my_accounts[_account.address] = {'account': _account, 'wallet': _wallet}
					except Exception as ex:
						messagebox.showerror(title='Error loading file', message=str(ex))

			_temp_my_main_account = self.select_my_acount_by_name(self.my_main_account.accountName, update=False)
			self.my_main_account = _temp_my_main_account if _temp_my_main_account is not None else self.my_main_account
		except Exception as ex:
			print('No database found', str(ex))

	def create_tabs(self):
		self.tab_control = ttk.Notebook(self.master)
		self.account_tab = tk.Frame(self.tab_control)
		self.create_tab = tk.Frame(self.tab_control)
		self.send_tab = tk.Frame(self.tab_control)
		self.messages_tab = tk.Frame(self.tab_control)
		self.info_tab = tk.Frame(self.tab_control)
		self.tab_control.add(self.account_tab, text='Accounts balances')
		self.tab_control.add(self.create_tab, text='Create Account')
		self.tab_control.add(self.send_tab, text='Send')
		self.tab_control.add(self.messages_tab, text='Messages')
		self.tab_control.add(self.info_tab, text='Accounts info')
		self.tab_control.pack(expand=1, fill='both')

	def create_info_tab(self):
		tk.Label(self.info_tab, text='Choose token name:', font=("Helvetica", 12)).grid(row=0, column=0, sticky=tk.W)
		self.tokens_cmb_info = ttk.Combobox(self.info_tab)
		_token = []
		_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
		self.tokens_cmb_info['values'] = _token
		self.tokens_cmb_info.set(_token[0])
		self.tokens_cmb_info.grid(column=0, row=1, sticky=tk.W)
		tk.Label(self.info_tab, text='Account by name:',
				 font=("Helvetica", 12)).grid(column=1, row=0, sticky=tk.W)
		self.my_accounts_cmb_info = ttk.Combobox(self.info_tab)
		_acc = []
		_acc.extend([acc['account'].accountName for acc in self.my_accounts.values()])
		self.my_accounts_cmb_info['values'] = _acc
		self.my_accounts_cmb_info.set(_acc[0])
		self.my_accounts_cmb_info.grid(column=1, row=1, sticky=tk.W)
		tk.Button(self.info_tab, text="Get Info", command=lambda: self.get_info(
			self.my_accounts_cmb_info.get(), self.tokens_cmb_info.get())).grid(column=2, row=0, rowspan=2, sticky=tk.W)

		self.info_txt = scrolledtext.ScrolledText(self.info_tab, width=120, height=30)
		self.info_txt.grid(column=0,row=3, columnspan=3)

	def get_info(self, account, token):
		self.info_txt.delete(1.0, tk.END)
		self.info_txt.insert(tk.INSERT, "Account: \n" + account+"\n")
		self.info_txt.insert(tk.INSERT, "Token: \n" + token+"\n")
		_account = self.select_my_acount_by_name(account)
		self.info_txt.insert(tk.INSERT, _account.show() + "\n")
		_token = self.chainnet.get_token_by_name(token)
		self.info_txt.insert(tk.INSERT, _token.show() + "\n")
		self.info_txt.insert(tk.INSERT, _token.showAll() + "\n")

	def create_account_tab(self):
		self.update_my_accounts()
		self.amounts = {}
		self.accounts_balances = {}
		for add, acc in self.my_accounts.items():
			self.add_new_account(add, acc['account'])

	def add_new_account(self, address, account):
		self.accounts_balances[address] = {}
		self.amounts[address] = {}
		self.column_nr[address] = len(self.column_nr)
		tk.Label(self.account_tab, text=account.accountName + "'s balances: ",
				 font=("Helvetica", 13), justify='right', relief="ridge",
				 bg="#ddd555000", fg="#fffffffff").grid(column=self.column_nr[address] * 2, row=0, columnspan=2)

		self.add_new_amounts(address, account)
		self.my_main_account.kade.save('my_main_accounts', str(list(self.my_accounts.keys())))
		self.update_amounts()


	def add_new_amounts(self, address, account):
		_row_nr = len(self.accounts_balances[address]) + 2
		for key, token in account.amount.items():
			if key not in self.amounts[address]:
				self.amounts[address][key] = tk.StringVar()
				self.accounts_balances[address][key] = tk.Label(self.account_tab, textvariable=self.amounts[address][key],
				                                            font=("Helvetica", 12), justify='right', relief="ridge",
																bg="#dddddd000", fg="#000000ddd")
				self.accounts_balances[address][key].grid(row=_row_nr, column=self.column_nr[address] * 2, sticky=tk.W)
				self.amounts[address][key+'l'] = tk.StringVar()
				self.accounts_balances[address][key+'l'] = tk.Label(self.account_tab, textvariable=self.amounts[address][key+'l'],
				                                            font=("Helvetica", 12), justify='right', relief="ridge",
																bg="#dddddd000", fg="#000000222")
				self.accounts_balances[address][key+'l'].grid(row=_row_nr, column=self.column_nr[address] * 2 + 1, sticky=tk.E)
				_row_nr += 1

	def create_send_tab(self):
		tk.Label(self.send_tab, text='Choose token name:',
								font=("Helvetica", 16)).grid(row=1, column=0)
		self.tokens_cmb = ttk.Combobox(self.send_tab)
		self.tokens_cmb['values'] = [str(token.accountName) for key, token in self.chainnet.tokens.items()]
		self.tokens_cmb.grid(row=2, column=0)
		tk.Label(self.send_tab, text='From account by name:',
								font=("Helvetica", 16)).grid(row=1, column=1)
		self.my_accounts_cmb = ttk.Combobox(self.send_tab)
		self.my_accounts_cmb['values'] = [acc['account'].accountName+' '+
		                                  ''.join(str(value)+' '+str(self.chainnet.get_token(key).accountName+' ')
		                                           for key, value in acc['account'].amount.items())
		                                  for acc in self.my_accounts.values()]
		self.my_accounts_cmb.grid(row=2, column=1)
		tk.Label(self.send_tab, text='To account by name:',
								font=("Helvetica", 16)).grid(row=4, column=1)
		self.send_address_ent = tk.Entry(self.send_tab, width=30, font=("Helvetica", 16))
		self.send_address_ent.grid(row=5, column=1)
		_amount = tk.DoubleVar()
		tk.Label(self.send_tab, text='Amount to send:',
								font=("Helvetica", 16)).grid(row=4, column=0)
		self.amount_spin = tk.Spinbox(self.send_tab, from_=0, to=100000000000, width=12, font=("Helvetica", 16), textvariable=_amount)
		self.amount_spin.grid(row=5, column=0)
		_amount.set(1)
		tk.Button(self.send_tab, text="Send", bg='orange', fg='blue', font=("Helvetica", 20),
									command=lambda: self.send_coins(self.my_accounts_cmb.get(),
																	self.send_address_ent.get(),
									                                self.amount_spin.get(),
									                                self.tokens_cmb.get())).grid(row=3, column=2, rowspan=2)
		tk.Button(self.send_tab, text="Attach", bg='yellow', fg='red', font=("Helvetica", 20),
									command=lambda: self.attach(self.send_address_ent.get(),
																self.my_accounts_cmb.get(),
									                                self.tokens_cmb.get())).grid(row=3, column=3, rowspan=2)

	def attach(self, account, attacher, token):
		try:
			self.update_my_accounts()
			account = self.select_my_acount_by_name(account)
			attacher = self.select_my_acount_by_name(attacher)
			token = self.chainnet.get_token_by_name(token)
			if attacher.address in token.chain.uniqueAccounts:
				if token.attach(account, attacher=attacher):
					self.add_new_amounts(account.address, account=account)
					self.update_amounts()
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
			self.update_my_accounts()
			from_account = self.select_my_acount_by_name(from_account)
			to_account = self.select_my_acount_by_name(to_account)#self.my_main_account.chain.uniqueAccounts[to_account]
			token = self.chainnet.get_token_by_name(token)
			if to_account.address in token.chain.uniqueAccounts and from_account.address in token.chain.uniqueAccounts:
				if from_account.send(to_account, token, amount):
					self.update_amounts()
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

		self.supply_spin = tk.Spinbox(self.create_tab, from_=1, to=1000000000000, width=20, textvariable=_amount)
		self.supply_spin.pack()
		_amount.set(1000000)
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

		self.update_my_accounts()
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
			_account.save()
			self.my_accounts[_account.address] = {'account': _account, 'wallet': _wallet}
			_acc = []
			_acc.extend([acc['account'].accountName for acc in self.my_accounts.values()])
			self.my_accounts_cmb_info.config(values=_acc)
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.add_new_account(_account.address, account=_account)
			self.update_amounts()
			messagebox.showinfo('Account created', _account.accountName + ' from now you are in Chainnet')

		if self.selected_account.get() == 2:
			_account = self.chainnet.baseToken.create(accountName=accountName, creator=self.my_main_account, address=address)
			messagebox.showinfo('Account created', _account.accountName + ' from now you are in Chainnet')

		if self.selected_account.get() == 3:
			_wallet = CWallet(accountName)
			_limitedToken = CLimitedToken(self.chainnet.DB, accountName, initSupply, creator=self.my_main_account, address=_wallet.pubKey, save=False)
			if _limitedToken is None:
				messagebox.showerror(title='Error in token creating', message='Token is not created')
				return
			self.my_main_account.save()
			_limitedToken.save()
			self.new_address_ent.delete(0, tk.END)
			self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
			self.new_address_ent.pack()
			self.my_accounts[_limitedToken.address] = {'account': _limitedToken, 'wallet': _wallet}
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.chainnet.add_token(_limitedToken)
			_token = []
			_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.tokens_cmb_info.config(values=_token)
			self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.add_new_account(_limitedToken.address, account=_limitedToken)
			self.add_new_amounts(self.my_main_account.address, account=_limitedToken)
			self.add_new_amounts(_limitedToken.address, account=_limitedToken)
			self.update_amounts()
			messagebox.showinfo('Limited Token is created', _limitedToken.accountName + ' is now created with total supply: '+str(_limitedToken.totalSupply))

		if self.selected_account.get() == 4:
			_wallet = CWallet(accountName)
			_actionToken = CActionToken(self.chainnet.DB, accountName, initSupply, creator=self.my_main_account, address=_wallet.pubKey, save=False)
			if _actionToken is None:
				messagebox.showerror(title='Error in token creating', message='Token is not created')
				return
			self.my_main_account.save()
			_actionToken.save()
			self.new_address_ent.delete(0, tk.END)
			self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
			self.new_address_ent.pack()
			self.my_accounts[_actionToken.address] = {'account': _actionToken, 'wallet': _wallet}
			self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
			self.chainnet.add_token(_actionToken)
			_token = []
			_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.tokens_cmb_info.config(values=_token)
			self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
			self.add_new_account(_actionToken.address, account=_actionToken)
			self.add_new_amounts(self.my_main_account.address, account=_actionToken)
			self.add_new_amounts(_actionToken.address, account=_actionToken)
			self.update_amounts()
			messagebox.showinfo('Action Token is created',
			                    _actionToken.accountName + ' is now created with initial supply: ' + str(
				                    _actionToken.totalSupply))

	def select_my_acount_by_name(self, name, update=True):

		if update: self.update_my_accounts()

		for add, acc in self.my_accounts.items():
			if acc['account'].accountName == name.split(' ')[0]:
				return acc['account']
		return None

	def update_amounts(self):
		self.update_my_accounts()
		for _acc in self.my_accounts:
			_account = self.my_accounts[_acc]['account']
			for key, amount in _account.amount.items():
				try:
					token_name = self.chainnet.tokens[key].accountName
					self.amounts[_acc][key].set(str(amount))
					self.amounts[_acc][key+'l'].set(' [ '+token_name+' ] ')
				except:
					pass

root = tk.Tk()
root.title("Chainnet Wallet App")

app = Application(master=root)
root.geometry('1000x600')
app.mainloop()