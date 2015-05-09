import socket, sys

class Bot(object):
	
	def __init__(self, chan, nick, serv='irc.freenode.net', port=6667, autojoin=False, silent=False):
		self.serv		= serv
		self.port		= port
		self.chan		= chan
		self.nick		= nick
		self.autojoin	= autojoin
		self.silent		= silent
		self.sock		= None
	
	def send_raw(self, msg):
		if self.sock == None:
			sys.sterr.write('Closed socket?\n')
			return False
		
		try:
			self.sock.send(msg.encode() +b'\n')
		except:
			e = sys.exc_info()[0]
			sys.stderr.write('Exception %s\n' % e)
			return False
				
	def send_msg(self, target, msg):
		return self.send_raw('PRIVMSG %s :%s' % (target, msg))
	
	def join(self):
		return self.send_raw('JOIN %s' % self.chan)
		
	def check_ping(self, msg):
		if msg.find('PING :') != -1:
			self.send_raw('PONG :pingis')
		else:
			return False
			
	def check_messages(self):
		msg = self.sock.recv(1024).decode().strip('\n\r')
		if not self.silent:
			print msg
		self.check_ping(msg)
		return msg
		
	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.serv, self.port))
		self.send_raw('USER {0} {0} {0} :Python IRC Bot'.format(self.nick))
		self.send_raw('NICK {0}'.format(self.nick))
		if self.autojoin:
			self.join()
		return self.sock
