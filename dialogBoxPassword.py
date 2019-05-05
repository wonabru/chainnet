import tkinter
from init_chainnet import CInitChainnet
from chainnet_run import Application
from wallet import CWallet
from tkinter import messagebox

class Mbox(object):

	root = None

	def __init__(self, msg, dict_key=None):
		"""
		msg = <str> the message to be displayed
		dict_key = <sequence> (dictionary, key) to associate with user input
		(providing a sequence for dict_key creates an entry for user input)
		"""
		if msg is None:
			return
		tki = tkinter
		self.top = tki.Toplevel(Mbox.root)

		frm = tki.Frame(self.top, borderwidth=4, relief='ridge')
		frm.pack(fill='both', expand=True)

		label = tki.Label(frm, text=msg)
		label.pack(padx=4, pady=4)

		caller_wants_an_entry = dict_key is not None

		if caller_wants_an_entry:
			self.entry = tki.Entry(frm)
			self.entry.pack(pady=4)

			b_submit = tki.Button(frm, text='Unlock')
			b_submit['command'] = lambda: self.entry_to_dict(dict_key)
			b_submit.pack()

		b_cancel = tki.Button(frm, text='Cancel')
		b_cancel['command'] = self.top.destroy
		b_cancel.pack(padx=4, pady=4)

	def change_password(self, dict_key):
		tki = tkinter
		self.top = tki.Toplevel(Mbox.root)

		frm = tki.Frame(self.top, borderwidth=4, relief='ridge')
		frm.pack(fill='both', expand=True)

		label = tki.Label(frm, text='Current password')
		label.pack(padx=4, pady=4)

		self.entry = tki.Entry(frm)
		self.entry.pack(pady=4)

		label = tki.Label(frm, text='New password')
		label.pack(padx=4, pady=4)

		self.entry_new = tki.Entry(frm)
		self.entry_new.pack(pady=4)

		label = tki.Label(frm, text='Repeat password')
		label.pack(padx=4, pady=4)

		self.entry_repeat = tki.Entry(frm)
		self.entry_repeat.pack(pady=4)


		b_current = tki.Button(frm, text='Apply change')
		b_current['command'] = lambda: self.entry_to_dict(dict_key)
		b_current.pack()

		b_cancel = tki.Button(frm, text='Cancel')
		b_cancel['command'] = self.top.destroy
		b_cancel.pack(padx=4, pady=4)


	def entry_to_dict(self, dict_key):
		data = self.entry.get()
		if data:
			d, key = dict_key
			d[key] = data
			if key == 'Password':
				if data != '' and CWallet().check_password(data) is False:
					messagebox.showerror('Password validation', 'Password validation fails')
				else:
					chainnet = CInitChainnet('@main', data)
					app = Application(master=self.root, chainnet=chainnet)
					self.root.geometry('1000x600')
					app.mainloop()
				self.top.destroy()

			elif key == 'current_password':
				if data != '' and CWallet().check_password(data) is False:
					messagebox.showerror('Password validation', 'Password validation fails')
				else:
					self.current_password = data
					self.new_password = self.entry_new.get()
					self.repeat_password = self.entry_repeat.get()
					if self.new_password == self.repeat_password:
						CWallet().change_password(self.current_password, self.new_password)
					else:
						messagebox.showerror('Password validation', 'New entry passwords do not match')
				self.top.destroy()