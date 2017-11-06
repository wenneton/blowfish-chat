import socket
import sys
import random
from threading import Thread


class Receive(Thread):

    def __init__ (self,conn, adr,i):
        Thread.__init__(self)
        self.conn = conn
        self.adr = adr
        self.i = i

    def run(self):
        global buff, buffnicks
        while True:
            rec = str(self.conn.recv(1024))
            print("[ip = " + str(adr[0])+ ", nick = " + nicks[self.i] + "] - " + rec[2:len(rec)-1])
            for j in range(len(buff)):
                if(self.i != j):
                    buff[j] = rec
                    buffnicks[j] = nicks[self.i]

class Send(Thread):

    def __init__ (self,conn,adr,i):
        Thread.__init__(self)
        self.conn = conn
        self.i = i
        self.adr = adr

    def run(self):
        global buff, ultMsg, adresses
        ultMsg[self.i] = buff[self.i]
        while True:
            if ultMsg[self.i] != buff[self.i]:
                buff[self.i] = bytes(buff[self.i], 'utf-8')
                ultMsg[self.i] = buff[self.i]
                self.conn.send(bytes(buffnicks[self.i],'utf-8'))
                self.conn.send(buff[self.i])

def geraChave():
    key = '0x'

    for i in range(8):
        key = key + hex(random.randint(0,15))[2]

    return key


try:
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit()
 
print('Socket Created')
 
HOST = socket.gethostname()
PORT = 5000

try:
    s.bind((HOST, PORT))
    print("bind ok")
except socket.error:
    print('Bind failed')
    sys.exit()

try:
    remote_ip = socket.gethostbyname(HOST) 
except socket.gaierror:
    #could not resolve
    print('Hostname could not be resolved. Exiting')
    sys.exit()

print(remote_ip)
s.listen(5)

conn, adr = s.accept()


key = geraChave()
print("Conectado com" + adr[0] + ": " + str(adr[1]) + " com a chave: " + key)
keyBytes = bytes(key,'utf-8')
conn.send(keyBytes)

buff = []
ultMsg = []
nicks = []
buffnicks = []
i = 0 #numero de clientes conectados -1
buff.append(bytes('conectado','utf-8'))
ultMsg.append(buff[i])
nick = str(conn.recv(1024))
nick = nick[2:len(nick)]
nicks.append(nick)
buffnicks.append(nick)


while True:
    a = Receive(conn, adr,i)
    a.start()

    b = Send(conn,adr,i)
    b.start()

    conn, adr = s.accept()
    print("Conectado com" + adr[0] + ": " + str(adr[1]) + " com a chave: " + key)
    conn.send(keyBytes)
    i = i + 1
    buff.append(bytes('conectado','utf-8'))
    ultMsg.append(buff[i])
    nick = str(conn.recv(1024))
    nick = nick[2:len(nick)]
    nicks.append(nick)
    buffnicks.append(nick)

print("saiu")

conn.close()
s.close()