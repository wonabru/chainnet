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
from transaction import CAtomicTransaction
import datetime as dt


class CFinish:
	finish = False

class Application(tk.Frame):
	def __init__(self, master, chainnet):
		super().__init__(master)
		self.chainnet = chainnet
		self.my_main_wallet = self.chainnet.wallet
		self.my_main_account = self.chainnet.my_account
		self.my_accounts = {}
		self.column_nr = {}
		self.my_accounts_names = {}
		self.master = master
		self.update_my_accounts()
		self.create_tabs()

		self.create_account_tab()
		self.create_create_tab()
		self.create_send_tab()
		self.create_receive_tab()
		self.create_info_tab()
		self.create_node_tab()
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
						_account.load_wallet()
						_account.update(with_chain=True)

						self.my_accounts[_account.address] = {'account': _account, 'wallet': _account.wallet}
						self.my_accounts_names[_account.address] = _account.accountName
					except Exception as ex:
						messagebox.showerror(title='Error updating account in update_my_accounts', message=str(ex))

			_temp_my_main_account = self.select_my_acount_by_name(self.my_main_account.accountName, update=False)
			self.my_main_account = _temp_my_main_account if _temp_my_main_account is not None else self.my_main_account
		except Exception as ex:
			print('No database found', str(ex))

	def create_tabs(self):
		self.tab_control = ttk.Notebook(self.master)
		self.account_tab = tk.Frame(self.tab_control)
		self.create_tab = tk.Frame(self.tab_control)
		self.send_tab = tk.Frame(self.tab_control)
		self.receive_tab = tk.Frame(self.tab_control)
		self.info_tab = tk.Frame(self.tab_control)
		self.node_tab = tk.Frame(self.tab_control)
		self.tab_control.add(self.account_tab, text='Accounts balances')
		self.tab_control.add(self.create_tab, text='Create Account')
		self.tab_control.add(self.send_tab, text='Send')
		self.tab_control.add(self.receive_tab, text='Receive')
		self.tab_control.add(self.info_tab, text='Accounts info')
		self.tab_control.add(self.node_tab, text='Nodes')
		self.tab_control.pack(expand=1, fill='both')

	def create_info_tab(self):
		tk.Label(self.info_tab, text='Choose token name:', font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W)
		self.tokens_cmb_info = ttk.Combobox(self.info_tab)
		_token = []
		_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
		self.tokens_cmb_info['values'] = _token
		self.tokens_cmb_info.set(_token[0])
		self.tokens_cmb_info.grid(column=0, row=1, sticky=tk.W)
		tk.Label(self.info_tab, text='Account by name:',
				 font=("Arial", 12)).grid(column=1, row=0, sticky=tk.W)
		self.my_accounts_cmb_info = ttk.Combobox(self.info_tab)
		_acc = []
		_acc.extend([acc['account'].accountName for acc in self.my_accounts.values()])
		self.my_accounts_cmb_info['values'] = _acc
		self.my_accounts_cmb_info.set(_acc[0])
		self.my_accounts_cmb_info.grid(column=1, row=1, sticky=tk.W)
		tk.Button(self.info_tab, text="Get local Info", command=lambda: self.get_info(
			self.my_accounts_cmb_info.get(), self.tokens_cmb_info.get())).grid(column=2, row=0, rowspan=2, sticky=tk.W)
		tk.Button(self.info_tab, text="Get Info from net", command=lambda: self.get_info(
			self.my_accounts_cmb_info.get(), self.tokens_cmb_info.get())).grid(column=4, row=0, rowspan=2, sticky=tk.W)
		self.info_txt = scrolledtext.ScrolledText(self.info_tab, width=120, height=30)
		self.info_txt.grid(column=0,row=3, columnspan=3)

	def create_node_tab(self):
		self.node_ent = tk.Entry(self.node_tab, width=20, font=("Arial", 16))
		self.node_ent.grid(row=1, column=0)
		tk.Button(self.node_tab, text="Add node",
		          command=lambda: self.add_node(self.node_ent.get())).grid(column=2, row=0, rowspan=2, sticky=tk.W)

		self.node_txt = scrolledtext.ScrolledText(self.node_tab, width=120, height=30)
		self.node_txt.grid(column=0, row=3, columnspan=3)

	def add_node(self, node):
		self.chainnet.DB.register_node(node)
		self.chainnet.DB.bootstrapNodes()

	def get_info(self, account, token):
		self.info_txt.delete(1.0, tk.END)
		self.info_txt.insert(tk.INSERT, "Account: \n" + account+"\n")
		self.info_txt.insert(tk.INSERT, "Token: \n" + token+"\n")
		_account = self.select_my_acount_by_name(account)
		self.info_txt.insert(tk.INSERT, _account.show() + "\n")
		_token = self.chainnet.get_token_by_name(token)
		self.info_txt.insert(tk.INSERT, _token.show() + "\n")
		self.info_txt.insert(tk.INSERT, _token.showAll() + "\n")

	def recreate_account_tab(self):
		self.update_amounts()
		self.account_tab.destroy()
		self.account_tab = tk.Frame(self.tab_control)
		self.tab_control.insert(0, self.account_tab, text='Accounts balances')
		self.tab_control.select(0)
		self.tab_control.pack()
		self.create_account_tab()

	def create_account_tab(self):

		tk.Button(self.account_tab, text="Update external accounts", bg='yellow',
				  command=self.update_amounts).grid(column=2, row=100, columnspan=2, sticky=tk.W)

		tk.Button(self.account_tab, text="Save and spread info on your accounts", bg='yellow',
				  command=self.save_all_my_accounts).grid(column=0, row=100, columnspan=2, sticky=tk.W)

		tk.Button(self.account_tab, text="Refresh graphic's interface", bg='yellow',
				  command=self.recreate_account_tab).grid(column=4, row=100, columnspan=2, sticky=tk.W)

		self.amounts = {}
		self.accounts_balances = {}
		self.accounts_names_lbl = {}
		_index = 0
		for add, acc in self.my_accounts.items():
			self.add_new_account(add, acc['account'], _index)
			_index += 1

	def save_all_my_accounts(self):
		def spread():
			for acc in self.my_accounts.values():
				acc['account'].save()

		for i in range(10):
			self.after(1000 * i, spread)

	def add_new_account(self, address, account, index):
		self.accounts_balances[address] = {}
		self.amounts[address] = {}
		self.accounts_names_lbl[account.address] = tk.StringVar()
		self.column_nr[address] = index
		tk.Label(self.account_tab, textvariable=self.accounts_names_lbl[account.address],
				 font=("Arial", 13), justify='right', relief="ridge",
				 bg="#ddd555000", fg="#fffffffff").grid(column=self.column_nr[address] * 2, row=0, columnspan=2)
		self.accounts_names_lbl[account.address].set(account.accountName + "'s balances: ")
		self.add_new_amounts(address, account)
		self.my_main_account.kade.save('my_main_accounts', str(list(self.my_accounts.keys())))
		self.update_amounts()


	def add_new_amounts(self, address, account):
		_row_nr = len(self.accounts_balances[address]) + 2
		for key, token in account.amount.items():
			if key not in self.amounts[address]:
				self.amounts[address][key] = tk.StringVar()
				self.accounts_balances[address][key] = tk.Label(self.account_tab, textvariable=self.amounts[address][key],
				                                            font=("Arial", 12), justify='right', relief="ridge",
																bg="#dddddd000", fg="#000000ddd")
				self.accounts_balances[address][key].grid(row=_row_nr, column=self.column_nr[address] * 2, sticky=tk.W)
				self.amounts[address][key+'l'] = tk.StringVar()
				self.accounts_balances[address][key+'l'] = tk.Label(self.account_tab, textvariable=self.amounts[address][key+'l'],
				                                            font=("Arial", 12), justify='right', relief="ridge",
																bg="#dddddd000", fg="#000000222")
				self.accounts_balances[address][key+'l'].grid(row=_row_nr, column=self.column_nr[address] * 2 + 1, sticky=tk.E)
				_row_nr += 1

	def create_receive_tab(self):
		tk.Label(self.receive_tab, text='Token name:',
								font=("Arial", 16)).grid(row=1, column=0)
		self.tokens_ent = tk.Entry(self.receive_tab, width=20, font=("Arial", 16))
		self.tokens_ent.grid(row=2, column=0)
		tk.Label(self.receive_tab, text='From account by address:',
								font=("Arial", 16)).grid(row=1, column=1)
		self.from_account_ent = tk.Entry(self.receive_tab, width=20, font=("Arial", 16))
		self.from_account_ent.grid(row=2, column=1)
		tk.Label(self.receive_tab, text='To account by address:',
								font=("Arial", 16)).grid(row=4, column=1)
		self.to_address_ent = tk.Entry(self.receive_tab, width=20, font=("Arial", 16))
		self.to_address_ent.grid(row=5, column=1)
		tk.Label(self.receive_tab, text='Amount to receive:',
								font=("Arial", 16)).grid(row=4, column=0)
		self.amount_ent = tk.Entry(self.receive_tab, width=20, font=("Arial", 16))
		self.amount_ent.grid(row=5, column=0)
		tk.Label(self.receive_tab, text='Deal must be closed till:',
								font=("Arial", 16)).grid(row=6, column=0)
		self.time_to_close_ent = tk.Entry(self.receive_tab, width=20, font=("Arial", 16))
		self.time_to_close_ent.grid(row=7, column=0)

		tk.Button(self.receive_tab, text="Check incomming transactions", bg='orange', fg='blue', font=("Arial", 20),
									command=self.in_background).grid(row=2, column=2, rowspan=2)
		tk.Button(self.receive_tab, text="Sign", bg='orange', fg='blue', font=("Arial", 20),
									command=lambda: self.sign_receive(self.to_address_ent.get())).grid(row=4, column=2, rowspan=2)

	def in_background(self):
		self.atomicTransaction = None
		self.look_for_deal()

		if self.atomicTransaction is not None:
			self.tokens_ent.delete(0, tk.END)
			self.tokens_ent.insert(0, self.atomicTransaction.token.accountName)
			self.from_account_ent.delete(0, tk.END)
			self.from_account_ent.insert(0, self.atomicTransaction.sender.address)
			self.to_address_ent.delete(0, tk.END)
			self.to_address_ent.insert(0, self.atomicTransaction.recipient.address)
			self.amount_ent.delete(0, tk.END)
			self.amount_ent.insert(0, str(self.atomicTransaction.amount))
			self.time_to_close_ent.delete(0, tk.END)
			self.time_to_close_ent.insert(0, self.atomicTransaction.time)

	def sign_receive(self, address):

		def loop(finish):
			_txn = DB.look_at('FinalTransaction:'+self.atomicTransaction.getHash()+':Transaction')
			if _txn is not None:
				_account.process_transaction(_txn, dt.datetime.today())
				finish.finish = True
				return
			finish.finish = False

		try:
			DB = self.my_main_account.kade
			_account = self.my_accounts[address]['account']
			_wallet = _account.load_wallet()
			_signature = _wallet.sign(self.atomicTransaction.getHash())
			DB.save(key=self.atomicTransaction.getHash(), value=_signature, announce='SignatureRecipient:')

			_finish = CFinish()

			for i in range(30):
				if _finish.finish == False:
					self.after(1000 * i, loop, _finish)
				else:
					break

			self.update_amounts()
			messagebox.showinfo(title='Receive with success', message=self.atomicTransaction.sender.accountName + ' sent ' +
																   str(self.atomicTransaction.amount) + ' of ' + self.atomicTransaction.token.accountName + ' to account ' +
																   self.atomicTransaction.recipient.accountName)
		except Exception as ex:
			self.showError(ex)

	def showError(self, ex):
		if len(ex.args) > 1:
			_title, _err = ex.args
		else:
			_title, _err = 'Other error', ex.args
		messagebox.showerror(title=str(_title), message=str(_err))

	def look_for_deal(self):
		try:
			_announcement = {}
			DB = self.my_main_account.kade
			_my_accounts = DB.get('my_main_accounts')
			if _my_accounts is None:
				_my_accounts = [self.my_main_account.address]
			else:
				_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))
			for acc in _my_accounts:
				_announcement[acc] = DB.look_at('AtomicTransaction:' + 'AtomicTransaction:' + acc)
				if _announcement[acc] is not None:
					self.atomicTransaction = CAtomicTransaction(CAccount(DB, '__temp1__', None, "1"),
											   CAccount(DB, '__temp2__', None, "2"),
											   -1, "",
											   CAccount(DB, '__temp3__', None, "3"))
					_messsage = _announcement[acc][:-1]
					self.atomicTransaction.setParameters(_messsage)
					self.atomicTransaction.sender.verify(_announcement[acc], self.atomicTransaction.sender.address)
		except Exception as ex:
			self.showError(ex)

	def create_send_tab(self):
		tk.Label(self.send_tab, text='Choose token name:',
								font=("Arial", 16)).grid(row=1, column=0)
		self.tokens_cmb = ttk.Combobox(self.send_tab)
		self.tokens_cmb['values'] = [str(token.accountName) for key, token in self.chainnet.tokens.items()]
		self.tokens_cmb.grid(row=2, column=0)
		tk.Label(self.send_tab, text='From account by name:',
								font=("Arial", 16)).grid(row=1, column=1)
		self.my_accounts_cmb = ttk.Combobox(self.send_tab)
		self.my_accounts_cmb['values'] = [acc['account'].accountName+' '+
		                                  ''.join(str(value)+' '+str(self.chainnet.get_token(key).accountName+' ')
		                                           for key, value in acc['account'].amount.items())
		                                  for acc in self.my_accounts.values()]
		self.my_accounts_cmb.grid(row=2, column=1)
		tk.Label(self.send_tab, text='To account by address:',
								font=("Arial", 16)).grid(row=4, column=1)
		self.send_address_ent = tk.Entry(self.send_tab, width=30, font=("Arial", 16))
		self.send_address_ent.grid(row=5, column=1)
		_amount = tk.DoubleVar()
		tk.Label(self.send_tab, text='Amount to send:',
								font=("Arial", 16)).grid(row=4, column=0)
		self.amount_spin = tk.Spinbox(self.send_tab, from_=0, to=100000000000, width=12, font=("Arial", 16), textvariable=_amount)
		self.amount_spin.grid(row=5, column=0)
		_amount.set(1)
		tk.Label(self.send_tab, text='Max waiting time in seconds:',
								font=("Arial", 16)).grid(row=6, column=0)
		self.waiting_time_ent = tk.Entry(self.send_tab, width=10, font=("Arial", 16))
		self.waiting_time_ent.insert(tk.END, '3600')
		self.waiting_time_ent.grid(row=7, column=0)
		tk.Button(self.send_tab, text="Lock Account", bg='orange', fg='blue', font=("Arial", 20),
									command=lambda: self.lock(self.my_accounts_cmb.get(),
																	self.send_address_ent.get(),
									                                self.tokens_cmb.get(),
									                                self.waiting_time_ent.get())).grid(row=1, column=2, rowspan=2)
		tk.Button(self.send_tab, text="Send", bg='orange', fg='blue', font=("Arial", 20),
									command=lambda: self.send_coins(self.my_accounts_cmb.get(),
																	self.send_address_ent.get(),
									                                self.amount_spin.get(),
									                                self.tokens_cmb.get(),
									                                self.waiting_time_ent.get())).grid(row=3, column=2, rowspan=2)
		tk.Button(self.send_tab, text="Attach recipient to Token", bg='yellow', fg='red', font=("Arial", 20),
									command=lambda: self.attach(self.send_address_ent.get(),
																self.my_accounts_cmb.get(),
									                                self.tokens_cmb.get())).grid(row=5, column=2, rowspan=2)

	def lock(self, my_account, other_account, token, waiting_time):
		try:
			self.update_my_accounts()
			my_account = self.select_my_acount_by_name(my_account)
			token = self.chainnet.get_token_by_name(token)
			_wallet = my_account.load_wallet()
			time_to_close = dt.datetime.today() + dt.timedelta(seconds=float(waiting_time))

			token.lockAccounts(my_account, _wallet.sign('Locking for deal: ' + my_account.address + ' + ' +
			                                          other_account + ' till ' + str(time_to_close)),
			                   other_account, time_to_close)

			_finish = CFinish()
			for i in range(30):
				if _finish.finish == False:
					self.after(1000 * i, token.lock_loop, my_account, other_account, time_to_close, _finish)
				else:
					break

			if time_to_close < dt.datetime.today():
					raise Exception('Lock Accounts fails', 'Could not found locked accounts till '+str(time_to_close))

			if _finish.finish:
				messagebox.showinfo('Lock with Success', 'Locking for deal: ' + my_account.address + ' + ' +
									other_account + ' till ' + str(time_to_close))
		except Exception as ex:
			self.showError(ex)

	def attach(self, account, attacher, token):
		try:
			self.update_my_accounts()
			account = self.my_accounts[account]['account']
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
			self.showError(ex)

	def send_coins(self, from_account, to_account, amount, token, wating_time):
		try:
			amount = float(amount)
			self.update_my_accounts()
			from_account = self.select_my_acount_by_name(from_account)
			to_account = self.my_accounts[to_account]['account']
			token = self.chainnet.get_token_by_name(token)
			if to_account.address in token.chain.uniqueAccounts:

				_finish = CFinish()
				atomic, time_to_close = from_account.send(to_account, token, amount, float(wating_time))
				for i in range(30):
					if _finish.finish == False:
						self.after(1000 * i, from_account.send_loop, to_account, atomic, time_to_close, _finish)
					else:
						break

				if time_to_close < dt.datetime.today():
					raise Exception('Sign Transaction fails',
									'Could not obtain valid signature from recipient till ' + str(time_to_close))

				if _finish.finish:
					messagebox.showinfo(title='Send with success', message=atomic.sender.accountName + ' sent ' +
										str(atomic.amount) + ' of ' + atomic.token.accountName + ' to account ' +
										atomic.recipient.accountName)

			else:
				messagebox.showerror(title='Send', message='You need first attach '+to_account.accountName+' to '+token.accountName)
		except Exception as ex:
			self.showError(ex)

	def radiobtn_change(self):

		if self.selected_account.get() == 1:
			self.lbl_initial_supply_pos.grid_remove()
			self.supply_spin.grid_remove()
			self.lbl_new_address.grid_remove()
			self.new_address_ent.grid_remove()
			self.create_new_account_btn_lbl.set("Create new account")
		if self.selected_account.get() in [2, 5,6]:
			self.lbl_initial_supply_pos.grid_remove()
			self.supply_spin.grid_remove()
			self.lbl_new_address.grid(row=6, column=0, sticky=tk.W)
			self.new_address_ent.grid(row=6, column=1, sticky=tk.W)
			self.create_new_account_btn_lbl.set("Invite account")
		if self.selected_account.get() == 3:
			self.set_initial_supply_lbl.set('Set Total Supply for Limited Token:')
			self.lbl_initial_supply_pos.grid(row=8, column=0, sticky=tk.W)
			self.supply_spin.grid(row=8, column=1, sticky=tk.W)
			self.lbl_new_address.grid_remove()
			self.new_address_ent.grid_remove()
			self.create_new_account_btn_lbl.set("Create new Limited Token")
		if self.selected_account.get() == 4:
			self.set_initial_supply_lbl.set('Set Initial Supply for Action Token:')
			self.lbl_initial_supply_pos.grid(row=8, column=0, sticky=tk.W)
			self.supply_spin.grid(row=8, column=1, sticky=tk.W)
			self.lbl_new_address.grid_remove()
			self.new_address_ent.grid_remove()
			self.create_new_account_btn_lbl.set("Create new Action Token")


	def create_create_tab(self):
		tk.Label(self.create_tab, text='Set account name:',
								font=("Arial", 16)).grid(row=4, column=0, sticky=tk.W)
		self.new_name_ent = tk.Entry(self.create_tab, width=30, font=("Arial", 16))
		self.new_name_ent.grid(row=4, column=1, sticky=tk.W)
		self.lbl_new_address = tk.Label(self.create_tab, text='Address:',
								font=("Arial", 16))
		self.new_address_ent = tk.Entry(self.create_tab, width=50, font=("Arial", 16))
		_amount = tk.DoubleVar()

		self.supply_spin = tk.Spinbox(self.create_tab, from_=0, to=1000000000000, width=20, textvariable=_amount)
		_amount.set(1000000)
		self.set_initial_supply_lbl = tk.StringVar()
		self.set_initial_supply_lbl.set('Hello')
		self.lbl_initial_supply_pos = tk.Label(self.create_tab, textvariable=self.set_initial_supply_lbl,
		                                       font=("Arial", 16))
		self.selected_account = tk.IntVar()
		self.selected_account.set(1)
		rad1 = tk.Radiobutton(self.create_tab, text='Create new simple account from scratch', value=1, bg='#fff000fff',
		                      variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad2 = tk.Radiobutton(self.create_tab, text='Invite simple account using public address', bg='#fff000eee',
					   value=2, variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad3 = tk.Radiobutton(self.create_tab, text='Create new Limited Token', bg='#fff000bbb',
					   value=3, variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad4 = tk.Radiobutton(self.create_tab, text='Create new Action Token', bg='#fff000999',
					   value=4, variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad5 = tk.Radiobutton(self.create_tab, text='Invite Limited Token using public address', bg='#fff000eee',
					   value=5, variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad6 = tk.Radiobutton(self.create_tab, text='Invite Action Token using public address', bg='#fff000eee',
					   value=6, variable=self.selected_account, command=lambda: self.radiobtn_change(), indicatoron=0)
		rad1.grid(row=0, column=0, sticky=tk.W)
		rad2.grid(row=0, column=1, sticky=tk.W)
		rad3.grid(row=1, column=0, sticky=tk.W)
		rad4.grid(row=2, column=0, sticky=tk.W)
		rad5.grid(row=1, column=1, sticky=tk.W)
		rad6.grid(row=2, column=1, sticky=tk.W)

		self.create_new_account_btn_lbl = tk.StringVar()
		self.create_new_account_btn_lbl.set("Create new account")
		tk.Button(self.create_tab, textvariable=self.create_new_account_btn_lbl, bg="#888000990", font=("Arial", 20),
									command=lambda: self.create_new_account(self.new_name_ent.get(),
																			self.new_address_ent.get(),
									                                        self.supply_spin.get())).grid(row=10, column=0,
		                                                                                                  columnspan=2,
		                                                                                                  rowspan=2)

	def get_my_accounts_names(self):
		return self.my_accounts_names.values()

	def create_new_account(self, accountName, address, initSupply):
		if accountName == '':
			messagebox.showwarning(title='Account name', message='Account name cannot be empty')
			return
		if self.selected_account.get() == 2 and CWallet().check_address(address) == False:
			messagebox.showwarning(title='Account address', message='Proper account address must be set')
			return

		self.update_my_accounts()
		if accountName in self.get_my_accounts_names():
			messagebox.showwarning(title='Account name', message='There is just such an account name in your wallet')
			return

		try:
			initSupply = float(initSupply)
			if self.selected_account.get() == 1:
				_wallet = CWallet(accountName)

				_account = self.chainnet.baseToken.create(accountName=accountName, creator=self.my_main_account, address=_wallet.pubKey)
				if _account is None:
					messagebox.showerror(title='Error in account creating', message='Account is not created')
					return
				'''
				self.new_address_ent.delete(0, tk.END)
				self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
				self.new_address_ent.grid(row=6, column=1, sticky=tk.W)
				'''
				_account.save()
				self.my_accounts[_account.address] = {'account': _account, 'wallet': _wallet}
				_acc = []
				_acc.extend([acc['account'].accountName for acc in self.my_accounts.values()])
				self.my_accounts_cmb_info.config(values=_acc)
				self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
				self.add_new_account(_account.address, account=_account, index=len(self.my_accounts))
				self.update_amounts()
				messagebox.showinfo('Account created', _account.accountName + ' from now you are in Chainnet')

			if self.selected_account.get() == 2:
				_account = self.chainnet.baseToken.invite(accountName=accountName, creator=self.my_main_account, address=address)
				_account.save()
				self.my_accounts[_account.address] = {'account': _account, 'wallet': None}
				_acc = []
				_acc.extend([acc['account'].accountName for acc in self.my_accounts.values()])
				self.my_accounts_cmb_info.config(values=_acc)
				self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
				self.add_new_account(_account.address, account=_account, index=len(self.my_accounts))
				self.update_amounts()
				messagebox.showinfo('Account added', _account.accountName + ' from now you are in Chainnet')

			if self.selected_account.get() in [3, 5]:
				if self.selected_account.get() == 3:
					_wallet = CWallet(accountName)
					_address = _wallet.pubKey
					_limitedToken = CLimitedToken(self.chainnet.DB, accountName, initSupply,
												  creator=self.my_main_account, address=_address, save=False)
				else:
					_wallet = None
					_limitedToken = self.my_main_account.inviteLimitedToken(accountName='__' + accountName, creator=self.my_main_account,
													 address=address)

				if _limitedToken is None:
					messagebox.showerror(title='Error in token creating', message='Token is not created')
					return
				self.my_main_account.save()
				_limitedToken.save()
				'''
				self.new_address_ent.delete(0, tk.END)
				self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
				self.new_address_ent.grid(row=6, column=1, sticky=tk.W)
				'''
				self.my_accounts[_limitedToken.address] = {'account': _limitedToken, 'wallet': _wallet}
				self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
				self.chainnet.add_token(_limitedToken)
				_token = []
				_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
				self.tokens_cmb_info.config(values=_token)
				self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
				self.add_new_account(_limitedToken.address, account=_limitedToken, index=len(self.my_accounts))
				self.add_new_amounts(self.my_main_account.address, account=_limitedToken)
				self.add_new_amounts(_limitedToken.address, account=_limitedToken)
				self.update_amounts()
				messagebox.showinfo('Limited Token is created', _limitedToken.accountName + ' is now created with total supply: '+str(_limitedToken.totalSupply))

			if self.selected_account.get() in [4, 6]:
				if self.selected_account.get() == 4:
					_wallet = CWallet(accountName)
					_address = _wallet.pubKey
					_actionToken = CActionToken(self.chainnet.DB, accountName, initSupply, creator=self.my_main_account,
												address=_address, save=False)
				else:
					_wallet = None
					_actionToken = self.my_main_account.inviteActionToken(accountName='__' + accountName,
																		creator=self.my_main_account,
																		address=address)
				if _actionToken is None:
					messagebox.showerror(title='Error in token creating', message='Token is not created')
					return
				self.my_main_account.save()
				_actionToken.save()
				'''
				self.new_address_ent.delete(0, tk.END)
				self.new_address_ent.insert(0, str(_wallet.pubKey)[:20])
				self.new_address_ent.grid(row=6, column=1, sticky=tk.W)
				'''
				self.my_accounts[_actionToken.address] = {'account': _actionToken, 'wallet': _wallet}
				self.my_accounts_cmb.config(values=[acc['account'].accountName for acc in self.my_accounts.values()])
				self.chainnet.add_token(_actionToken)
				_token = []
				_token.extend([str(token.accountName) for key, token in self.chainnet.tokens.items()])
				self.tokens_cmb_info.config(values=_token)
				self.tokens_cmb.config(values=[str(token.accountName) for key, token in self.chainnet.tokens.items()])
				self.add_new_account(_actionToken.address, account=_actionToken, index=len(self.my_accounts))
				self.add_new_amounts(self.my_main_account.address, account=_actionToken)
				self.add_new_amounts(_actionToken.address, account=_actionToken)
				self.update_amounts()
				messagebox.showinfo('Action Token is created',
				                    _actionToken.accountName + ' is now created with initial supply: ' + str(
					                    _actionToken.totalSupply))

		except Exception as ex:
			self.showError(ex)

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
					self.accounts_names_lbl[_account.address].set(_account.accountName+'\'s balances')
					self.amounts[_acc][key].set(str(amount))
					self.amounts[_acc][key+'l'].set(' [ '+token_name+' ] ')
				except:
					pass

global chainnet

if __name__ == '__main__':

	root = tk.Tk()
	root.title("Chainnet Wallet App")

	chainnet = CInitChainnet()

	app = Application(master=root, chainnet=chainnet)
	root.geometry('1000x600')
	app.mainloop()