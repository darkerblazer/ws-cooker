#!/bin/python3

# NOTE: Made without utilizing any slopware, the modules might have some slopware influence tho.

# NOTE: Cryptography functions in this script are for proof of concept, for mission critical applications use something other than os.urandom!

import sys
import threading
import socket
import time
import base64
import zlib
import ssl
import random
import os

try: from websocket import create_connection
except: sys.stderr.write("ERROR: from websocket import create_connection\n")

try: from cryptography.fernet import Fernet
except: sys.stderr.write("ERROR: from cryptography.fernet import Fernet\n")

ChaCha20Poly1305 = print
AESGCMSIV = print
AESSIV = print
AESGCM = print
AESCCM = print
AESOCB3 = print

try: from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCMSIV, AESGCM, AESSIV, AESCCM, AESOCB3
except: sys.stderr.write("ERROR: from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCMSIV, AESGCM, AESSIV, AESCCM, AESOCB3\n")

class Node_Base64:
	'<b85d|b64d|b32d|b16d|b85e|b64e|b32e|b16e>'

	buf   = b''

	def __init__(self, a):
		self.bfunc = {'b85d': base64.b85decode,'b64d': base64.b64decode,'b32d': base64.b32decode,'b16d': base64.b16decode,'b85e': base64.b85encode,'b64e': base64.b64encode,'b32e': base64.b32encode,'b16e': base64.b16encode}[a]
		self.ulock = threading.Barrier(2)

	def recv(self, i=10200000): # i is disregarded
		self.ulock.wait()
		return self.buf

	def send(self, i):
		self.buf = self.bfunc(i)
		self.ulock.wait()

	def is_closed(self): return False

	def close(self): pass

	def spawn_one(self, i=None): return self

	def rununtil_one(self, i=None):
		try: return self
		finally: self.rununtil_one = abs

class Node_Null(Node_Base64):
	'null, everything is nulled'

	def __init__(self, a=""): pass

	def recv(self, i=10200000): pass

	def send(self, i=10200000): pass

class Node_Split(Node_Base64):
	'<id>'

	buf   = []
	bfunc = {}

	def __init__(self, a):
		self.ulock = threading.Lock()
		a1 = self.bfunc
		if a in a1:
			threading.Thread(target=pushp, args=(self.recv, a1[a].send)).start()
			threading.Thread(target=pushp, args=(a1[a].recv, self.send)).start()
		else: a1[a] = self

	def recv(self, i=10200000):
		while not self.buf: time.sleep(1)
		try:
			self.ulock.acquire()
			return self.buf.pop(0)
		finally: self.ulock.release()

	def send(self, i):
		try:
			self.ulock.acquire()
			self.buf += [ i ]
		finally: self.ulock.release()

class Node_Spliter(Node_Split):
	'<class:args>'

	def __init__(self, a):
		a = a.split(':')
		a[1] = ":".join(a[1:])
		self.bfunc = globals()[a[0]](a[1])
		self.ulock = threading.Lock()
		self.buf   = []
		threading.Thread(target=pushp, args=(self.recv, self.bfunc.send)).start()
		threading.Thread(target=pushp, args=(self.bfunc.recv, self.send)).start()

class Node_Any(Node_Base64):
	'<module.any>'

	def __init__(self, a):
		a = a.split('.')
		self.bfunc = globals()[a[0]].__dict__[a[1]]
		self.ulock = threading.Barrier(2)

class Node_Any2(Node_Base64):
	'<module.any> <method>'

	def __init__(self, a):
		a = a.split(' ')
		a[0] = a[0].split('.')
		self.bfunc = globals()[a[0][0]]

		def _(a, bfunc=self.bfunc.__dict__[a[0][1]], a1=self.bfunc.__dict__[a[1]]): return bfunc(a, a1)

		self.bfunc = _
		self.ulock = threading.Barrier(2)

class Node_Fernet(Node_Any):
        '<e|d> <base64:key(32)>'

        def __init__(self, a="e"):
                a1 = a.split(' ')
                a = ['e', 'ItmPdeU+0slzKDPwxTbAOVCpvDBLCJhyMhW8PqePEFE=']
                for i in range(len(a1)): a[i] = a1[i]

                a1 = Fernet(a[1].encode("utf-8"))
                self.bfunc = {"e": a1.encrypt, "d": a1.decrypt}[a[0][0]]
                self.ulock = threading.Barrier(2)

class Node_Fernet_ChaCha20Poly1305(Node_Any):
        '<e|d|es|ds> <base64:key(32)> <number> <aad>'

        nauth = ChaCha20Poly1305
        nonce = 12
        noncef = os.urandom

        def __init__(self, a="e"):
                a1 = a.split(' ')
                a = ['e', 'ItmPdeU+0slzKDPwxTbAOVCpvDBLCJhyMhW8PqePEFE=', '123', 'gahh hhhhh hhhhh'] + ["" for i in range(len(a1))]
                for i in range(len(a1)): a[i] = a1[i]

                a[3] = " ".join(a[3:]).strip()

                a1 = self.nauth(base64.b64decode(a[1]))
                self.bfunc = {"e": a1.encrypt, "d": a1.decrypt}[a[0][0]]   # possible land mines ahead

                if a[0] == 'es':
                        def _(a, bfunc=self.bfunc, aad=a[3].encode("utf-8"), nonce=self.nonce, noncef=self.noncef):
                               a1 = noncef(nonce)
                               return a1+bfunc(a1, a, aad)
                elif a[0] == 'ds':
                        def _(a, bfunc=self.bfunc, aad=a[3].encode("utf-8"), nonce=self.nonce): return bfunc(a[:nonce], a[nonce:], aad)
                else:
                    def _(a, bfunc=self.bfunc, rand=random.Random(int(a[2])), aad=a[3].encode("utf-8"), nonce=self.nonce): return bfunc(rand.randbytes(nonce), a, aad)

                self.bfunc = _
                self.ulock = threading.Barrier(2)

class Node_Fernet_AESSIV(Node_Fernet_ChaCha20Poly1305):
        '<e|d|es|ds> <base64:key(512)> <number> <aad>'

        nauth = AESSIV
        nonce = 16

        def __init__(self, a="e"):
                a1 = a.split(' ')
                a = ['e', 'ItmPdeU+0slzKDPwxTbAOVCpvDBLCJhyMhW8PqePEFE=', '123', 'gahh hhhhh hhhhh'] + ["" for i in range(len(a1))]
                for i in range(len(a1)): a[i] = a1[i]

                a[3] = " ".join(a[3:]).strip()

                a1 = self.nauth(base64.b64decode(a[1]))
                self.bfunc = {"e": a1.encrypt, "d": a1.decrypt}[a[0][0]]   # possible land mines ahead

                if a[0] == 'es':
                        def _(a, bfunc=self.bfunc, aad=a[3].encode("utf-8"), nonce=self.nonce, noncef=self.noncef):
                               a1 = noncef(nonce)
                               return a1+bfunc(a, [aad, a1])
                elif a[0] == 'ds':
                        def _(a, bfunc=self.bfunc, aad=a[3].encode("utf-8"), nonce=self.nonce): return bfunc(a[nonce:], [aad, a[:nonce]])
                else:
                     def _(a, bfunc=self.bfunc, rand=random.Random(int(a[2])), aad=a[3].encode("utf-8"), nonce=self.nonce): return bfunc(a, [aad, rand.randbytes(nonce)])

                self.bfunc = _
                self.ulock = threading.Barrier(2)

class Node_Fernet_AESGCMSIV(Node_Fernet_ChaCha20Poly1305):
	'<e|d|es|ds> <base64:key(128)> <number> <aad>'

	nauth = AESGCMSIV
	nonce = 12

class Node_Fernet_AESGCM(Node_Fernet_ChaCha20Poly1305):
	'<e|d|es|ds> <base64:key(128)> <number> <aad>'

	nauth = AESGCM
	nonce = 12

class Node_Fernet_AESCCM(Node_Fernet_ChaCha20Poly1305):
	'<e|d|es|ds> <base64:key(128)> <number> <aad>'

	nauth = AESCCM
	nonce = 13

class Node_Fernet_AESOCB3(Node_Fernet_ChaCha20Poly1305):
	'<e|d|es|ds> <base64:key(128)> <number> <aad>'

	nauth = AESOCB3
	nonce = 12

class Node_GOD(Node_Any):  # make a new class by expanding on Node_Any class, you can choose any class that fits
	'<text>'

	def __init__(self, a=""):
		if not a: a="An explosion is a rapid expansion in volume of a given amount of matter associated with an extreme outward release of energy, usually with the generation of high temperatures and release of high-pressure gases. Explosions may also be generated by a slower expansion that would normally not be forceful, but is not allowed to expand, so that when whatever is containing the expansion is broken by the pressure that builds as the matter inside tries to expand, the matter expands forcefully. An example of this is a volcanic eruption created by the expansion of magma in a magma chamber as it rises to the surface. Supersonic explosions created by high explosives are known as detonations and travel through shock waves. Subsonic explosions are created by low explosives through a slower combustion process known as deflagration. For an explosion to occur, there must be a rapid, forceful expansion of matter. There are numerous ways this can happen, both naturally and artificially, such as volcanic eruptions, or two objects striking each other at very high speeds, as in an impact event. Explosive volcanic eruptions occur when magma rises from below, it has dissolved gas in it. The reduction of pressure as the magma rises causes the gas to bubble out of solution, resulting in a rapid increase in volume, however the size of the magma chamber remains the same. This results in pressure buildup that eventually leads to an explosive eruption. Explosions can also occur outside of Earth in the universe in events such as supernovae, or, more commonly, stellar flares. Humans are also able to create explosions through the use of explosives, or through nuclear fission or fusion, as in a nuclear weapon. Explosions frequently occur during bushfires in eucalyptus forests where the volatile oils in the tree tops suddenly combust."
		# constructor, this function will be called when `test = Node_GOD()`, and `self` will be returned to `test`

		a = [ i.lower() for i in a.split(" ") if i ]
		self.wordbank = [[],[]]
		for i in a:
			if i not in self.wordbank[0]: self.wordbank[0] += [i]

		for i in self.wordbank[0]: self.wordbank[1] += [[]]

		i1 = len(a)
		try:
			for i in range(i1): self.wordbank[1][self.wordbank[0].index(a[i])] += [self.wordbank[0].index(a[i+1])]
		except: self.wordbank[1][self.wordbank[0].index(a[i])] += [self.wordbank[0].index(a[0])]

		# print(self.wordbank)

		# since we dont have a function to call, we create one right here

		def god(a, words=self.wordbank):
			try: i=int(a.decode("utf-8"))
			except: i=10
			i1 = random.choice(random.choice(words[1]))
			a = words[0][i1]
			for i in range(i):
				i2 = random.choice(words[1][i1])
				a += " " + words[0][i2]
				i1 = i2
			return a.strip().encode("utf-8")


		self.bfunc = god

		#  inits from Node_Any class

		self.ulock = threading.Barrier(2)


class Node_owo(Node_Any):
	'<text>'

	def __init__(self, a=""):

		# since we dont have a function to call, we create one right here
		def owo(a): return a.replace(b'l', b'w').replace(b'r', b'w')

		self.bfunc = owo

		#  inits from Node_Any class

		self.ulock = threading.Barrier(2)

class Node_nya(Node_Any):
	'<text>'

	def __init__(self, a=""):

		def nya(a): return a.replace(b'no', b'nyo').replace(b'. ', b' nya~~. ')

		self.bfunc = nya

		#  inits from Node_Any class

		self.ulock = threading.Barrier(2)

class Node_Log(Node_Base64):
	'<self.send -> stderr>'

	def __init__(self, a="", ulock=threading.Lock()):
		def _(a, ulock=ulock):
			try:
				ulock.acquire()
				sys.stderr.buffer.write(a)
				return a
			finally: ulock.release()
		self.bfunc = _
		self.ulock = threading.Barrier(2)

class Node_WS(Node_Base64):
	'<url> <init>'

	def __init__(self, a):
		if isinstance(a, str): a = a.split(' ')
		a1 = a
		a = ['ws://0.0.0.0:8000/ws', 'default_channel']
		for i in range(len(a1)): a[i] = a1[i]

		self.argv = a
		self.ws = create_connection(a[0])
#		self.send = self.ws.send_binary
		self.close = self.ws.close
		self.ws.send(a[1])

	def recv(self, i=10200000):
		try:
			a = self.ws.recv()
			if isinstance(a, str): a = a.encode("utf-8")
			if a: return a
			a = self.ws.recv()
			if isinstance(a, str): a = a.encode("utf-8")
			return a
		except Exception as e:
			sys.stderr.write(f"Node_WS::recv: {e}\n")
			time.sleep(random.randint(2,4) * 0.5)
			self.ws = Node_WS(self.argv).ws
			a = self.ws.recv()
			if isinstance(a, str): a = a.encode("utf-8")
			if a: return a
			a = self.ws.recv()
			if isinstance(a, str): a = a.encode("utf-8")
			return a

	def send(self, a):
		try: return self.ws.send_binary(a)
		except Exception as e:
			sys.stderr.write(f"Node_WS::send: {e}\n")
			time.sleep(random.randint(5,6) * 0.5)
			return self.ws.send_binary(a)

	def is_closed(self): return not self.ws.connected

class Spawn_WS(Node_WS):
	'<url> <init>'

	def rununtil_one(self, i=10200000): return Node_WS([self.argv[0], self.recv().decode("utf-8")])

	def spawn_one(self, i=None):
		if not i: i=time.time()
		i = self.argv[1] + "-" + str(i)
		try: return Node_WS([self.argv[0], i])
		finally:
			self.send(i.encode("utf-8"))
			time.sleep(1)

class Node_Zlib(Node_Base64):
	'<d|c>'

	def __init__(self, a):
		self.bfunc = {'d': zlib.decompress, 'c': zlib.compress}[a[0]]
		self.ulock = threading.Barrier(2)

class Node_Sleep(Node_Base64):
	'<number>'
	def __init__(self, a):
		self.bfunc = int(a)
		self.ulock = threading.Barrier(2)

	def send(self, i):
		self.buf = i
		time.sleep(self.bfunc)
		self.ulock.wait()

class Node_TCP(Node_Base64):
	'socket || <4|6> <0.0.0.0> <8080> <c|l|sc|sl> <ECDHE+AESGCM:!ECDSA> <./cabundle.pem> <./private.key>'
	def __init__(self, a):
		if isinstance(a, str):
			a1 = a.split(' ')
			a = ['4', '0.0.0.0', '8080', 'c', 'ECDHE+AESGCM:!ECDSA', './cabundle.pem', './private.key']
			for i in range(len(a1)): a[i] = a1[i]

			if a[0].lower().startswith('6'): sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			else: sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if a[3].lower().startswith('sc'):
				context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				context.load_verify_locations(a[5])
				context.set_ciphers(a[4])
				sock = context.wrap_socket(sock, server_hostname='localhost')
				sock.connect((a[1], int(a[2])))
			elif a[3].lower().startswith('sl'):
				sock.bind((a[1], int(a[2])))
				sock.listen(1)
				context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
				context.load_cert_chain(a[5], a[6])
				context.set_ciphers(a[4])
				sock = context.wrap_socket(sock, server_side=True).accept()[0]
			elif a[3].lower().startswith('c'): sock.connect((a[1], int(a[2])))
			else:
				sock.bind((a[1], int(a[2])))
				sock.listen(1)
				sock = sock.accept()[0]
			a = sock
		self.sock = a
		self.send = self.sock.send
		self.close = self.sock.close

	def recv(self, i=10200000):   # for self.sock._closed
		i =  self.sock.recv(i)
		if i: return i
		self.close()
		return i

	def is_closed(self): return self.sock._closed

	def spawn_one(self, i=None): return Node_TCP(i)

class Spawn_TCP(Node_TCP):
	'<4|6> <0.0.0.0> <8080> <c|l>'
	def __init__(self,  a):
		a1 = a.split(' ')
		a = ['4', '0.0.0.0', '8080']
		for i in range(len(a1)): a[i] = a1[i]

		if a[0].lower().startswith('6'): sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		else: sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((a[1], int(a[2])))
		sock.listen(1)
		self.sock = sock
		self.close = self.sock.close

	def rununtil_one(self, i=10200000): return Node_TCP(self.sock.accept()[0])

class Spawn_TCP_SSL(Spawn_TCP):
	'<4|6> <0.0.0.0> <8080> <ECDHE+AESGCM:!ECDSA> <./certchain.pem> <./private.key>'
	def __init__(self, a):
		a1 = a.split(' ')
		a = ['4', '0.0.0.0', '8443', 'ECDHE+AESGCM:!ECDSA', './certchain.pem', './private.key']   # adding defaults
		for i in range(len(a1)): a[i] = a1[i]

		if a[0].lower().startswith('6'): sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		else: sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((a[1], int(a[2])))
		sock.listen(1)

		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.load_cert_chain(a[4], a[5])
		context.set_ciphers(a[3])

		self.sock = context.wrap_socket(sock, server_side=True)
		self.close = self.sock.close

class Node_UDP(Node_Base64):
	'socket || <4|6> <0.0.0.0> <8080>'
	def __init__(self, a):
		if isinstance(a, str):
			a1 = a.split(' ')
			a = ['4', '0.0.0.0', '8080']
			for i in range(len(a1)): a[i] = a1[i]
			if a[0].lower().startswith('6'): sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
			else: sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sockdest = (a[1], int(a[2]))
			a = sock
		self.sock = a

	def recv(self, i=10200000): return self.sock.recv(i)
		
	def send(self, i): return self.sock.sendto(i, self.sockdest)

	def spawn_one(self, i=None): return Node_UDP(i)

class Spawn_UDP(Node_UDP):
	'<4|6> <0.0.0.0> <8080>'
	def __init__(self, a):
		a1 = a.split(' ')
		a = ['4', '0.0.0.0', '8080']
		for i in range(len(a1)): a[i] = a1[i]
		if a[0].lower().startswith('6'): sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		else: sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((a[1], int(a[2])))
		self.sock = sock
		self.known = {}

	def rununtil_one(self, i = 10200000):
		while True:
			a = self.sock.recvfrom(i)
			if a[1] in self.known:
				try:
					self.known[a[1]][1].acquire()
					self.known[a[1]][0] += [a[0]]
					self.known[a[1]][2].set()
				finally: self.known[a[1]][1].release()
			else:
				self.known[a[1]] = [[a[0]], threading.Lock(), threading.Event()]

				sock = Node_UDP(self.sock)     # kind of a hack
				sock.sockdest = a[1]

				sys.stderr.write(f"Spawn_UDP::rununtil_one: {a[0]} {a[1]}\n")

				self.known[a[1]][2].set()

				def _(i=i, a=self.known[a[1]]):
					while not a[0]: a[2].wait()
					a[2].clear()
					try:
						a[1].acquire()
						return a[0].pop(0)
					finally: a[1].release()
				sock.recv = _

				return sock

def Spawn_WS2(a, argv={}):
	'wraps Spawn_WS'
	sys.stderr.write(f"main::Spawn_WS2: {a}\n")
	a1 = a
	if not isinstance(a,str): a = str(a)
	try: argv[a][1] = a1
	except:
		try: argv[a] = [Spawn_WS, a1]
		except: argv = {a:  [Spawn_WS, a1]}
		argv[a][0] = argv[a][0](a1)

	return argv[a][0].spawn_one()

class Spawn_IO(Node_Base64):
	'stdout/stdin'
	def __init__(self, a="", ulock=[threading.Lock(),threading.Lock()]):
		self.ulock = ulock
	def recv(self, i=10200000):
		try:
			self.ulock[0].acquire()
			return sys.stdin.buffer.read(i)
		finally: self.ulock[0].release()
	def send(self, i):
		try:
			self.ulock[1].acquire()
			return sys.stdout.buffer.write(i)
		finally: self.ulock[1].release()

def pushp(bfunc, afunc):
	a = bfunc()
	while a:
		afunc(a)
		a = bfunc()
	sys.stderr.write(f"main::pushp:return: {afunc} {bfunc}\n")

def pushl(afunc,clist=[]):
	afunc = afunc[0](afunc[1])
	sys.stderr.write(f"main::pushl: {afunc}\n")
	while True:
		a1 = afunc.rununtil_one()
		sys.stderr.write(f"main::pushl:while: {a1}\n")
		a3 = a1
		for i in clist:
			a2 = a3
			a3 = i[0](i[1])
			sys.stderr.write(f"main::pushl:for: {a3}\n")
			time.sleep(1)
			threading.Thread(target=pushp, args=(a2.recv, a3.send)).start()
		time.sleep(1)
		threading.Thread(target=pushp, args=(a3.recv, a1.send)).start()

def lpushp(afunc):
	a = ""
	for i in afunc:
		if a: i.send(a)
		a = i.recv()
	sys.stderr.write(f"main::lpushp: {a}\n")
	while True:
		for i in afunc:
			if a: i.send(a)
			else: return
			a = i.recv()
	sys.stderr.write(f"main::lpushp:return: {afunc}\n")

def lpushl(afunc,clist=[], clist1=[[],False]):
	afunc = afunc[0](afunc[1])
	sys.stderr.write(f"main::lpushl: {afunc}\n")
	while True:
		a1 = afunc.rununtil_one()
		sys.stderr.write(f"main::lpushl:while: {a1}\n")
		a1 = [ a1 ]
		a1 += [ i[0](i[1]) for i in clist ]
		if clist1[1]:
			while clist1[0]: time.sleep(1)
		clist1[0] = a1
		time.sleep(1)
		threading.Thread(target=lpushp, args=(a1,)).start()

if "__main__" == __name__:

	argv = {'map': []}

	i = 0

	while len(sys.argv[1:]) > i:
		if '--' == sys.argv[1:][i]:
			try: argv['map'] += [sys.argv[1:][i+1]]
			except: i=i+1
			break
		if sys.argv[1:][i].startswith('--'):
			try: argv[sys.argv[1:][i][2:]] += [sys.argv[1:][i+1]]
			except:
				try: argv[sys.argv[1:][i][2:]] = [sys.argv[1:][i+1]]
				except:
					try: argv[sys.argv[1:][i][2:]] += [1]
					except: argv[sys.argv[1:][i][2:]] = [1]
					i=i-1
			i=i+1
		else:
			try: argv['map'] += [sys.argv[1:][i]]
			except: break
		i=i+1


	pglobal = globals()

	if 'pushmap' not in pglobal:
		def pushmap(argv):
			if True: pass
			sys.stderr.write("available commands:\n\t" + "\n\t".join([f"{i}:{argv[i].__doc__}" for i in argv if i[:3] in ["Nod", "Spa"]]) + "\n")
			sys.stderr.write("\nexample:\n\tSpawn_UDP:4 0.0.0.0 8080\n\tSpawn_IO:\n\n")
			# a = sys.stdin.readline()
			a = input()
			aa = [a]
			while a:
				a = input()
				aa += [a]
			return aa	

	if 'cli' not in argv: argv['map'] = [ i.strip() for i in pushmap(pglobal) if i.strip() ]

	pushmap = [ [pglobal[i[:i.index(':')]],i[i.index(':')+1:].strip()] for i in argv['map'] ]

	pushl(pushmap.pop(0), pushmap)
