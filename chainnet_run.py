import tkinter as tk
from tkinter import ttk
from init_chainnet import CInitChainnet

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.chainnet = CInitChainnet()
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
		for key, token in self.chainnet.first_account.amount.items():
			self.amounts[key] = tk.StringVar()
			self.accounts_balances[key] = tk.Label(self.account_tab, textvariable=self.amounts[key],
												   font=("Helvetica", 16), padx=0).pack()


	def create_create_tab(self):
		self.address = tk.Label(self.create_tab, text='Set new address:',
								font=("Helvetica", 16)).pack()
		self.new_account = tk.Entry(self.create_tab, width=50, font=("Helvetica", 16)).pack()
		self.create_btn = tk.Button(self.create_tab, text="Create new Account", command=self.create_new_account).pack()

	def create_new_account(self, accountName, ):
		self.chainnet.baseToken.create()



	def update_amounts(self):
		for key, token in self.chainnet.first_account.amount.items():
			token_name = self.chainnet.tokens[key].accountName
			self.amounts[key].set(str(token) + '  ' + token_name)

root = tk.Tk()
root.title("Chainnet Wallet App")
root.geometry('600x400')
app = Application(master=root)

app.mainloop()