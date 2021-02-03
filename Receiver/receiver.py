import imaplib as im
import email
from contextlib import contextmanager
from datetime import datetime
from dateutil import parser as dparser

class Message:
	def __init__(self,kwargs):
		self.sender 	= kwargs.get("sender" )
		self.subject 	= kwargs.get("subject")
		self.when 		= kwargs.get("when", 0)
		self.data 		= kwargs.get("data")
		self.file		= kwargs.get("filename")
		self.isbin		= kwargs.get("binary",True)
		self.id = hex(id(self))[2:]

	def __repr__(self):
		return f"Message({self.id})"

	def __str__(self):
		get = lambda x,y: x if x is not None or x is not 0 else y
		return "{} - {} (file: {}, time: {}): {}".format(
			get(self.sender,"UNKNOWN"),
			'NO SUBJECT'
			if self.subject is None
			else f"\"{self.subject}\"",
			get(self.file,"None"),
			datetime.fromtimestamp(int(self.when)),
			get(self.data,"NO MESSAGE") 
			if len(self.data) <= 255 and not isinstance(self.data,bytes) 
			else "TOO LONG")
	
@contextmanager
def createConnection(hostname, port, username, password, verbose=False):
	if verbose: print('Connecting to: ' + hostname)
	try:
		server = im.IMAP4_SSL(hostname,port)
		if verbose: print("Connection secured!")
		if verbose: print('Signing in as: ' + username)
		server.login(username,password)
		if verbose: print('Succesfully signed in!')
		yield server # give it back to the user
		if verbose: print("Closing connection...")
		server.expunge() # make sure deleted emails are really deleted
		server.close() # stop selecting inboxes
		server.logout() # logout
	except Exception as err:
		raise Exception(f"[createConnection] {str(err)}").with_traceback(err.__traceback__)
	finally:
		del server

def getAllMessages(con=None):
	try:
		_, msg = con.select("INBOX")
		_, mails = con.search(None, 'ALL')
		for m in mails[0].decode("utf-8").split(" "):
			_, msg = con.fetch(m,'BODY.PEEK[]')
			mail = email.message_from_string(msg[0][1].decode("utf-8"))
			headers = dict(mail._headers)
			for bit in mail.walk():
				if bit.get("Content-Disposition") is not None:
					nd = {
						"sender":headers["From"],
						"when":dparser.parse(headers["Date"]).timestamp(),
						"data":bit.get_payload(decode=True)
						if bit.get_filename().split(".")[1] != "txt"
						else bit.get_payload(),
						"filename":bit.get_filename(),
						"binary":bit.get_filename().split(".")[1] != "txt"
					}
					if headers["Subject"] != "":
						nd["subject"] = headers["Subject"]
					yield Message(nd)
	except Exception:
		return None
		
def deleteAllEmails(con):
	_, _ = con.select("INBOX")
	_, data = con.search(None, 'ALL')
	for num in data[0].split():
		con.store(num, '+FLAGS', '\\Deleted')

