import socket
import sys
from threading import Thread

class Receive(Thread):

    def __init__ (self,conn):
        Thread.__init__(self)
        self.conn = conn

    def run(self):
        while True:
        	nick = str(self.conn.recv(1024))
        	nick = nick[2:len(nick)-2]


        	rec = self.conn.recv(1024)

        	rec = str(rec)
        	rec = rec[4:len(rec)-2]
        	msgCript = separaHexa(rec)

        	msg = ''

        	for i in range(len(msgCript)):
                    msg = msg + hex_to_str(BlowfishDecrypt(msgCript[i]))

        	#print('pos cript: ',rec)
        	print(">> " + nick + ': ' + msg)

class Send(Thread):

    def __init__ (self,conn):
        Thread.__init__(self)
        self.conn = conn

    def run(self):
        while True:
            msg = input()
            msg = separaString(msg)

            msgCript = []

            for i in range(len(msg)):
            	T = msg[i]
            	if len(T) <= 4:
            		T = T + '    '
            	msgCript.append(Blowfish(str_to_hex(T)))

            msg = ''
            for i in range(len(msgCript)):
            	msg = msg + msgCript[i][2:18]

            msg = bytes(msg, 'utf-8')
            self.conn.send(msg)


def Blowfish(T): #T tem 16 dígitos hexadecimais (64 bits)
	if len(T) < 18:
		zeros = ''
		for i in range(18-len(T)):
			zeros = zeros + '0'
		T = '0x' + zeros + T[2:len(T)]


	xL = int(T[2:10],16)
	xR = int(T[10:18],16)

	for i in range(16):
		xL = xL ^ int(p[i],16) #xor bit a bit
		xR = F(xL) ^ xR
		xL, xR = xR, xL
	xL, xR = xR, xL
	xR = xR ^ int(p[16],16)
	xL = xL ^ int(p[17],16)
	xR = hex(xR)
	xL = hex(xL)

	if len(xL) == 9:
		xL = '0x0' + xL[2:9]
	elif len(xL) == 8:
		xL = '0x00' + xL[2:8]
	if len(xR) == 9:
		xR = '0x0' + xR[2:9]
	elif len(xR) == 8:
		xR = '0x00' + xR[2:8]


	return xL + xR[2:10]

def BlowfishDecrypt(CC):
	LL = int(CC[0:8],16)
	RR = int(CC[8:16],16)

	LL = LL ^ int(p[17],16)
	for i in range(16,0,-2):
		RR = RR ^ F(LL) ^ int(p[i],16)
		LL = LL ^ F(RR) ^ int(p[i-1],16)
	RR = RR ^ int(p[0],16)

	RR = hex(RR)
	LL = hex(LL)

	"""if len(RR) == 9:
		RR = '0x0' + RR[2:9]
	elif len(RR) == 8:
		RR = '0x00' + RR[2:8]"""
	if len(LL) == 9:
		LL = '0x0' + LL[2:9]
	elif len(LL) == 8:
		LL = '0x00' + LL[2:8]

	return RR + LL[2:10]


def F(A):
	if A == 0:
		A = '0x00000000'
	else:
		A = hex(A)

	if(len(A) == 7):
		A = '0x000' + A[2:7]
	elif(len(A) == 8):
		A = '0x00' + A[2:8]
	elif(len(A) == 9):
		A = '0x0' + A[2:9]
	elif(len(A) == 6):
		A = '0x0000' + A[2:6]


	a = int(A[2:4],16)
	b = int(A[4:6],16)
	c = int(A[6:8],16)
	d = int(A[8:10],16)

	B = (((int(s1[a],16) + int(s2[b],16) % 2**32) ^ int(s3[c],16)) + int(s4[d],16)) % 2**32

	return B

def geraSubchaves(key):
	file = open("pi_in_hex.txt", "r")
	pi_hex = file.read() #string com as primeiros 8336 casas hexadecimas de pi
	file.close()

	"""
	Inicialização dos p's e S-boxes
	"""
	global p
	global s1,s2,s3,s4

	for i in range(18):#gera as 18 subchaves [p0...p17]
		p.append('0x' + pi_hex[i*8:(i+1)*8])

	for i in range(18,274):
		s1.append('0x' + pi_hex[i*8:(i+1)*8])

	for i in range(274,530):
		s2.append('0x' + pi_hex[i*8:(i+1)*8])

	for i in range(530,786):
		s3.append('0x' + pi_hex[i*8:(i+1)*8])

	for i in range(786,1042):
		s4.append('0x' + pi_hex[i*8:(i+1)*8])

	#key = '77efbac4' #chave de 32 bits (2012199620)
	#k = ''

	for i in range(18):
		p[i] = hex(int(key,16) ^ int(p[i],16))



	T = '0x0000000000000000'

	for i in range(0, 18, 2):
		T = Blowfish(T)
		p[i] = T[0:10]
		p[i+1] = '0x' + T[10:18]

	for i in range(0, 256, 2):
		T = Blowfish(T)
		s1[i] = T[0:10]
		s1[i+1] = '0x' + T[10:18]

	for i in range(0, 256, 2):
		T = Blowfish(T)
		s2[i] = T[0:10]
		s2[i+1] = '0x' + T[10:18]

	for i in range(0, 256, 2):
		T = Blowfish(T)
		s3[i] = T[0:10]
		s3[i+1] = '0x' + T[10:18]

	for i in range(0, 256, 2):
		T = Blowfish(T)
		s4[i] = T[0:10]
		s4[i+1] = '0x' + T[10:18]

	file = open('subkeys.txt', 'w')
	file.write(key + '\n')
	for i in range(len(p)-1):
		file.write(p[i] + ',')
	file.write(p[17])

	file.write('\n')

	for i in range(len(s1)-1):
		file.write(s1[i] + ',')
	file.write(s1[255])

	file.write('\n')

	for i in range(len(s2)-1):
		file.write(s2[i] + ',')
	file.write(s2[255])

	file.write('\n')

	for i in range(len(s3)-1):
		file.write(s3[i] + ',')
	file.write(s3[255])

	file.write('\n')

	for i in range(len(s4)-1):
		file.write(s4[i] + ',')
	file.write(s4[255])

	file.close()

def getSubchaves(key):

	global p
	global s1,s2,s3,s4

	file = open("subkeys.txt", 'r')
	subkeys = file.read()
	if len(subkeys) > 0:
		subkeys = subkeys.split('\n')
		if subkeys[0] == key:
			p = subkeys[1].split(',')
			s1 = subkeys[2].split(',')
			s2 = subkeys[3].split(',')
			s3 = subkeys[4].split(',')
			s4 = subkeys[5].split(',')
		else:
			geraSubchaves(key)
	else:
		geraSubchaves(key)


def str_to_hex(key):
	key_hex = '0x'
	for i in range(len(key)):
		aux = hex(ord(key[i]))
		key_hex = key_hex + aux[2:len(aux)]
	return key_hex

def hex_to_str(key):
	key_str = ''
	for i in range(2,len(key),2):
		key_str = key_str + chr(int(key[i:i+2],16))
	return key_str

def separaString(s):
	pedacos = []
	if len(s) <=8:
		pedacos.append(s)
	elif len(s) % 8 == 0:
		for i in range(0,len(s),8):
			pedacos.append(s[i:i+8])
	else:
		for i in range(0,(int(len(s)/8))*8,8):
			pedacos.append(s[i:i+8])
		pedacos.append(s[i+8:len(s)])
	return pedacos

def separaHexa(s):
	pedacos = []
	if len(s) <= 16:
		pedacos.append(s)
	elif len(s) % 16 == 0:
		for i in range(0,len(s),16):
			pedacos.append(s[i:i+16])
	else:
		for i in range(0,(int(len(s)/16))*16,16):
			pedacos.append(s[i:i+16])
		pedacos.append(s[i+16:len(s)])
	return pedacos


p = []
s1 = []
s2 = []
s3 = []
s4 = []

#geraSubchaves('0x646e6367') #teste


try:
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except socket.error:
	print("Falha ao criar socket")
	sys.exit()

host = socket.gethostname()
#host = "172.30.11.130"
port = 5000

try:
	remote_ip = socket.gethostbyname(host)
except socket.gaierror:
	print("Hostname nao encontrado. Saindo")
	sys.exit()

print(remote_ip)
s.connect((host,port))
key = s.recv(1024)
key = str(key)
key = key[2:len(key)-1]
print(key)
getSubchaves(key)


nick = input("Digite seu nome de usuário em até 10 caracteres: ")
print("Socket connectado em " + host + " no ip " + remote_ip + " com a chave: " + key + " e nick: " + nick)
nick = bytes(nick, 'utf-8')
s.send(nick)



a = Receive(s)
a.start()

b = Send(s)
b.start()

while True:
	pass

