from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import threading
import time

v_client = [{0: threading.Lock()},{},{},{}]

def handleMessage(a, a1, a2, a3, a4):
	try:
		a3.acquire()
		i1 = 1
		try:
			if b'_' in a4: i1 = int(a4.split(b"_")[0].decode("utf-8"))
			elif a4.startswith(b"++"):
				try: a2[2][a4] += a1
				except: a2[2][a4] = a1
				return
			elif a4[0] == 43:
				a4 = b"++" + a4[1:]
				try:
					a2[1][a4].acquire()
					a2[2][a4] = a1
					return
				finally: a2[1][a4].release()
			elif a4[0] == 45:
				a4 = b"++" + a4[1:]
				try:
					a2[1][a4].acquire()
					a.sendMessage(a2[2][a4])
					return
				finally: a2[1][a4].release()
			elif a4[0] == 38:
				a4 = a4[1:].split(b'-')
				a5 = a4.pop(0)
				a2 = a2[3]
				a2[a5] = a
				for i in a4:
					while True:
						try:
							a2[i].sendMessage(a1)
							break
						except: time.sleep(1)
				return
		except Exception as e1: print(f"handleMessage::try: {e1} {a4}")
		if i1 < 1: i1 = 1
		a5 = [a]
		a2 = a2[0]
		while i1 > 0:
			try:
				a2[0].acquire()
				for i in a2:
					if i not in a5 and a2[i] == a4:
						a5 += [i]
						try:
							i.sendMessage(a1)
							i1 = i1 - 1
						except Exception as e1: print(f"handleMessage::for:try: {e1} {i}")
			finally: a2[0].release()
			if i1 > 0: time.sleep(1)
	finally: a3.release()

class SimpleEcho(WebSocket):
    def handleMessage(self):
        try:
            global v_client
            v_client[0][0].acquire()
            if isinstance(self.data, str): self.data = self.data.encode("utf-8")
            if self not in v_client[0]:
                i = b" "
                try:
                    i = self.data.index(i)
                    v_client[0][self] = self.data[:i]
                    self.data = self.data[i + 1 :]
                except:
                    v_client[0][self] = self.data
                    self.data = b""
                if v_client[0][self] not in v_client[1]: v_client[1][v_client[0][self]] = threading.Lock()
            if self.data: threading.Thread(target=handleMessage, args=(self, self.data, v_client, v_client[1][v_client[0][self]], v_client[0][self])).start()
        except Exception as e1:
            print(f"handleMessage:: {e1} {self}")
        finally: v_client[0][0].release()

    def handleClose(self):
        try:
            global v_client
            v_client[0][0].acquire()
            v_client[0].pop(self)
        except Exception as e1:
            print(f"close:: {e1} {self}")
        finally: v_client[0][0].release()


if __name__ == "__main__":
	server = SimpleWebSocketServer("", 8000, SimpleEcho)
	server.serveforever()
