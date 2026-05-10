#!/bin/python3

# NOTE: Made without utilizing any slopware, the modules might have some slopware influence tho.

# NOTE: Cryptography functions in this script are for proof of concept, for mission critical applications use something other than os.urandom!

from wscooker import *

import tkinter

# from tkinter import ttk


### some changes to add pausing and breaks

def pushp(bfunc, afunc, tevent1, tevent2):
	a = bfunc()
	while a:
		tevent1.wait()
		if not tevent2.wait(timeout=1): break
		afunc(a)
		a = bfunc()
	sys.stderr.write(f"main::pushp:return: {afunc} {bfunc}\n")

def pushl(afunc,clist=[], tevent1=1, tevent2=1, lol=[]):
	try:
		tevent1.wait()
		afunc = afunc[0](afunc[1])
		sys.stderr.write(f"main::pushl: {afunc}\n")
		while True:
			a1 = afunc.rununtil_one()
			tevent1.wait()
			if not tevent2.wait(timeout=1): break
			sys.stderr.write(f"main::pushl:while: {a1}\n")
			a3 = a1
			for i in clist[1:]:
				a2 = a3
				a3 = i[0](i[1])
				sys.stderr.write(f"main::pushl:for: {a3}\n")
				time.sleep(1)
				threading.Thread(target=pushp, args=(a2.recv, a3.send, tevent1, tevent2)).start()
			time.sleep(1)
			threading.Thread(target=pushp, args=(a3.recv, a1.send, tevent1, tevent2)).start()
	except Exception as e:
		sys.stderr.write(f"main::pushl:except: {e}\n")
		lol[-1] = e
		afunc.close()

####

### UI specific functions

list_of_nods_spas_thread = []

def get_start_func(a, *a1, **a2):
	def _(a=a,a1=a1,a2=a2): return a(*a1, **a2)
	return _

def get_safe_thread_start_func(a, *a1, a2=threading.Lock()):
	def _(a=a,a1=a1,a2=a2):
		try:
			a2.acquire()
			return a(*a1)
		finally: a2.release()
	return threading.Thread(target=_).start

def get_safe_thread_start_func_loop(a, *a1):
	def _(a=a,a1=a1): return get_safe_thread_start_func(a, *a1)()
	return _

def get_thread_start_func_loop(a, *a1):
	def _(a=a,a1=a1): return get_thread_start_func(a, *a1)()
	return _

def safe_thread_start_func(a, *a1): return get_safe_thread_start_func(a, *a1)()

def thread_start_func(a, *a1): return threading.Thread(target=a, args=[*a1]).start()

def get_thread_start_func(a, *a1): return threading.Thread(target=a, args=[*a1]).start

def dont_throw_func(a, *a1):
	try: return a(*a1)
	except: sys.stderr.write(f"main::dont_throw_func: {a} {a1}\n")

def get_available_commands():
	globalz = globals()
	return [globalz[i] for i in globalz if i[:3] in ["Nod", "Spa"]] # I love this filter lol :3

def get_available_commands_str(i=None):
	globalz = globals()
	if i is None: return [i for i in globalz if i[:3] in ["Nod", "Spa"]]
	else: return [i for i in globalz if i[:3] in ["Nod", "Spa"]][i]

def get_length_of_available_commands(): return len(get_available_commands())

def get_activated_id(i, i2=None):
	globalz = globals()

	i1    = [0,0,[ [ globalz[i.split(":")[0].strip()], ":".join(i.split(":")[1:]).strip()] for i in i.strip().split("\n") if i.strip() and not i.strip().startswith("#") ],threading.Event(),threading.Event(),0]
	i1[1] = i1[2][0]

	for i3 in globalz["list_of_nods_spas_thread"]:
		if i1[2] in i3:
			sys.stderr.write("get_activated_id:: an ID with the same configuration exists.\n")
			return 0

	if i2 is not None:
		i3 = globalz["list_of_nods_spas_thread"][i2][2]
		i4 = i1[2]
		for i in range(abs(len(i4)-len(i3))): i3 += [[]]
		for i in range(len(i3)):
			try: i3[i] = i4[i]
			except: i3.pop(-1)
		while not i3[-1]: i3.pop(-1)
		return i2

	i1[-1] = i1
	i1[0] = threading.Thread(target=pushl, args=[*i1[1:]])

	# cant efford to have an exception here
	dont_throw_func(i1[3].clear)
	dont_throw_func(i1[4].set)

	i1[0].start()

	for i in range(len(globalz["list_of_nods_spas_thread"])):
		if not globalz["list_of_nods_spas_thread"][i][-1]:
			globalz["list_of_nods_spas_thread"][i] = i1
			return i

	globalz["list_of_nods_spas_thread"] += [i1]
	return 	len(globalz["list_of_nods_spas_thread"]) - 1

def activate_id(i):
	globalz = globals()

	i1 = globalz["list_of_nods_spas_thread"][i]
	i1[-1] = i1
	i1[0] = threading.Thread(target=pushl, args=[*i1[1:]])

	dont_throw_func(i1[3].clear)
	dont_throw_func(i1[4].set)

	i1[0].start()

def clear_id(i):
	globalz = globals()

	if globalz["list_of_nods_spas_thread"][i][0].is_alive(): return 0

	globalz["list_of_nods_spas_thread"][i][-1] = 0
	cancel_id(i)

def pause_id(i):
	globalz = globals()

	dont_throw_func(globalz["list_of_nods_spas_thread"][i][3].clear)
	dont_throw_func(globalz["list_of_nods_spas_thread"][i][4].set)

def resume_id(i):
	globalz = globals()

	dont_throw_func(globalz["list_of_nods_spas_thread"][i][4].set)
	dont_throw_func(globalz["list_of_nods_spas_thread"][i][3].set)

def cancel_id(i):
	globalz = globals()

	dont_throw_func(globalz["list_of_nods_spas_thread"][i][4].clear)
	dont_throw_func(globalz["list_of_nods_spas_thread"][i][3].set)

def is_id_alive(i): return globals()["list_of_nods_spas_thread"][i][0].is_alive()
def is_id_paused(i): return globals()["list_of_nods_spas_thread"][i][3].is_set()
def is_id_canceled(i): return globals()["list_of_nods_spas_thread"][i][4].is_set()
def get_id(i): return globals()["list_of_nods_spas_thread"][i]

####

class CookingUI:

	width  = 600
	height = 600
	box    = 32
	textoff= 4 #   ( 32 - font size ) / 2
	nods=[]
	junk=[]
	publish=0
	ws=0
	wsurl="ws://0.0.0.0:8000/ws"
	config_append = "++config"
	config_get = "-config"
	config_put = "+config"

	def __init__(self):

		self.window = tkinter.Tk()
		self.set_geometry()
		self.set_add_button()
		self.mainloop = self.window.mainloop
		self.window.protocol("WM_DELETE_WINDOW", self.close)

	def set_geometry(self): self.window.geometry(f"{self.width}x{self.height}")
	def check_update(self):
		if not self.publish: return
		self.window.after(10000, self.check_update)
		if self.ws:
			self.update_nods()
			return
		self.ws=1
		def _(self=self):
			try:
				self.ws = Node_WS([self.wsurl,self.config_append])
				self.ws1 = Node_WS([self.wsurl,self.config_get])
				self.ws2 = Node_WS([self.wsurl,self.config_put])
				while self.publish:
					time.sleep(10)
					self.ws.send(b"\0" + "\0".join([ "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]) for a in self.nods ]).encode("utf-8") + b"\0")
					self.ws1.send(b"1")
					a1 = [ i.decode("utf-8").strip() for i in self.ws1.recv().split(b'\0') if i ] + [ "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]) for a in self.nods ]
					for i in a1:
						i = get_activated_id(i)
						if i not in self.nods: self.nods += [i]
					time.sleep(10)
					self.ws.send(b"\0" + "\0".join([ "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]) for a in self.nods ]).encode("utf-8") + b"\0")
					self.ws1.send(b"1")
					a1 = [ i.decode("utf-8").strip() for i in self.ws1.recv().split(b'\0') if i ] + [ "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]) for a in self.nods ]
					for i in a1:
						i = get_activated_id(i)
						if i not in self.nods: self.nods += [i]
					self.ws2.send(b"\0" + "\0".join([ "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]) for a in self.nods ]).encode("utf-8") + b"\0")
			finally: self.ws = 0
		try:
			_ = threading.Thread(target=_)
			return _
		finally: _.start()
	def publish_mode(self):
		if self.publish:
			self.publish=0
			return
		self.publish=1
		self.check_update()
	def get_geometry(self): pass
	def clear(self):
		for i in self.junk: self.junk.pop(0).destroy()
	def update_nods(self):
		self.clear()
		for i in range(len(self.nods)):
			i2 = -1
			for i1 in [
tkinter.Button(self.window, text="x", command=get_start_func(clear_id, self.nods[i])),
tkinter.Button(self.window, text="c", command=get_start_func(cancel_id, self.nods[i])),
tkinter.Button(self.window, text="p", command=get_start_func(pause_id, self.nods[i])),
tkinter.Button(self.window, text="r", command=get_start_func(resume_id, self.nods[i])),
tkinter.Button(self.window, text="a", command=get_start_func(activate_id, self.nods[i])),
tkinter.Button(self.window, text="e", command=get_start_func(self.edit_entry, self.nods[i])),
tkinter.Label(self.window, text="{}: {}".format(self.nods[i], get_id(self.nods[i])[2]))
]:
				i2 += 1
				i1.place(x=self.box*i2, y=self.box*i+self.box)
				self.junk += [i1]
			i1.place(x=self.box*i2+self.textoff, y=self.box*i+self.box+self.textoff)

	def set_add_button(self):
		self.get_geometry()
		add_button = tkinter.Button(self.window, text = "+", command=self.add_entry)
		publish_button = tkinter.Button(self.window, text = "P", command=self.publish_mode)
		url_button = tkinter.Button(self.window, text = "<", command=self.publish_url_set)
		url_config = tkinter.Button(self.window, text = "C", command=self.publish_url_set_config)
		add_label = tkinter.Label(self.window, text = "x = clear, c = cancel, p = pause, r = resume (needs to first be resumed), a = activate (check if its activated first by resuming the thread), e = edit")
		add_button.place(x=0, y=0)
		publish_button.place(x=self.box, y=0)
		url_button.place(x=self.box*2, y=0)
		url_config.place(x=self.box*3, y=0)
		add_label.place(x=self.box*4+self.textoff, y=self.textoff)

	def publish_url_set_config(self):
		top = tkinter.Toplevel(self.window)
		entry = tkinter.Text(top)
		entry.insert(tkinter.END, self.config_append + '\n' + self.config_get + '\n' + self.config_put + '\n' )
		entry.place(x=0,y=self.box)

		def _(entry=entry, top=top, self=self):
			i = [ i for i in entry.get("1.0", tkinter.END).split("\n") if i ]
			self.config_append = i[0]
			self.config_get = i[1]
			self.config_put = i[2]
			top.destroy()

		tkinter.Button(top, text = "+", command=_).place(x=0,y=0)
		tkinter.Label(top, text = "Change the config of the publishing websocket").place(x=self.box+self.textoff, y=self.textoff)

	def publish_url_set(self):
		top = tkinter.Toplevel(self.window)
		entry = tkinter.Text(top)
		entry.insert(tkinter.END, self.wsurl)
		entry.place(x=0,y=self.box)

		def _(entry=entry, top=top, self=self):
			self.wsurl = [ i for i in entry.get("1.0", tkinter.END).split("\n") if i ][0]
			top.destroy()

		tkinter.Button(top, text = "+", command=_).place(x=0,y=0)
		tkinter.Label(top, text = "Change the URL of the publishing websocket").place(x=self.box+self.textoff, y=self.textoff)

	def add_entry(self):
		top = tkinter.Toplevel(self.window)
		entry = tkinter.Text(top)
		entry.insert(tkinter.END, "# Comment out, order them, and update the arguments:\n" + "\n".join([f"# {i.__name__}: {i.__doc__}" for i in get_available_commands()  if i.__name__[:3] in ["Nod", "Spa"]]))
		entry.place(x=0,y=self.box)

		def _(entry=entry, top=top, self=self):
			i = get_activated_id(entry.get("1.0", tkinter.END))
			if i not in self.nods: self.nods += [i]
			top.destroy()
			self.update_nods()

		tkinter.Button(top, text = "+", command=_).place(x=0,y=0)
		tkinter.Label(top, text = "Add a Push Link").place(x=self.box+self.textoff, y=self.textoff)

	def edit_entry(self, a):
		top = tkinter.Toplevel(self.window)
		entry = tkinter.Text(top)
		entry.insert(tkinter.END, "# Comment out, order them, and update the arguments:\n" + "\n".join([f"{i[0].__name__}: {i[1]}" for i in get_id(a)[2] ]))
		entry.place(x=0,y=self.box)
		
		def _(entry=entry, top=top, self=self, a=a):
			get_activated_id(entry.get("1.0", tkinter.END), a)
			top.destroy()
			self.update_nods()

		tkinter.Button(top, text = "+", command=_).place(x=0,y=0)
		tkinter.Label(top, text = f"Edit Push Link ID: {a}").place(x=self.box+self.textoff, y=self.textoff)

	def close(self):
		try: self.window.destroy()
		finally: os.kill(os.getpid(),9)

if "__main__" == __name__: CookingUI().mainloop()

