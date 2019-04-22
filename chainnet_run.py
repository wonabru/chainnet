import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from init_chainnet import CInitChainnet
from wallet import CWallet

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.chainnet = CInitChainnet()
		self.my_main_account = self.chainnet.my_account
		self.my_accounts = {}
		self.master = master
		self.pack()
		self.create_tabs()
		self.create_account_tab()
		self.create_create_tab()
		self.update_amounts()

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
		self.address = tk.Label(self.account_tab, text='Address: '+str(self.chainnet.wallet.pubKey[:20]),
								font=("Helvetica", 16), anchor=tk.W).pack()
		self.address = tk.Label(self.account_tab, text='Balances:', font=("Helvetica", 16), anchor=tk.W).pack()
		self.accounts_balances = {}
		self.amounts = {}
		for key, token in self.my_main_account.amount.items():
			self.amounts[key] = tk.StringVar()
			self.accounts_balances[key] = tk.Label(self.account_tab, textvariable=self.amounts[key],
												   font=("Helvetica", 16), padx=0).pack()


	def create_create_tab(self):
		self.selected_account = tk.IntVar()
		rad1 = tk.Radiobutton(self.create_tab, text='Create new account from scratch', value=1, variable=self.selected_account)
		rad2 = tk.Radiobutton(self.create_tab, text='Create new account using public address',
					   value=2, variable=self.selected_account)
		rad1.pack()
		rad2.pack()
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

	def create_new_account(self, accountName, address):
		if self.selected_account.get() == 1:
			_wallet = CWallet()
			_wallet.
			self.new_address_ent.config(state='disabled', text=)
		_account = self.chainnet.baseToken.create(accountName=accountName, creator=self.my_main_account, address=address)
		messagebox.showinfo('Account created',_account.accountName + ' from now you are in Chainnet')


	def update_amounts(self):
		for key, token in self.chainnet.first_account.amount.items():
			token_name = self.chainnet.tokens[key].accountName
			self.amounts[key].set(str(token) + '  ' + token_name)

root = tk.Tk()
root.title("Chainnet Wallet App")

app = Application(master=root)
root.geometry('600x400')
app.mainloop()