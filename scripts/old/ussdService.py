# telnet program example
import datetime
import select
import socket
import sys
import threading
import time
import xml.etree.ElementTree as ET

import json
import requests
from scripts import EmailService
from scripts.frappeclient import FrappeClient
from scripts.messageService import MessageSerice
from scripts.old import MessageProcessor

exitFlag = 0
accessDetails = open('/home/hemant/access.txt')
aD = json.loads(accessDetails.read())

# print aD
def logMe(msg):
	localtime = datetime.datetime.now().replace(microsecond=0)
	message = "[" + localtime.strftime("%Y-%m-%d %H:%M:%S") + "] " + msg + "\r\n"
	sys.stdout.write(message)
	sys.stdout.flush()


class USSDListernerThread(threading.Thread):
	"""docstring for USSDListernerThread"""

	def __init__(self, name):
		threading.Thread.__init__(self)
		# self.sock = sock
		self.name = name
		self.messenger = MessageSerice()

	def run(self):
		# logMe("Started " + self.name)
		exitFlag = 0
		USSDClient(self.messenger)

	# print "Exiting " + self.name
	def stop(self):
		# logMe("Trying to stop " + self.name)
		exitFlag = 1
		self.run = False


class USSDMessageProcessorThread(threading.Thread):
	"""docstring for USSDMessageProcessorThread"""

	def __init__(self, sessionid, msisdn, rootMsg, requestMsg, msgType, timeRec):
		threading.Thread.__init__(self)
		self.sessionid = sessionid
		self.msisdn = msisdn
		self.rootMsg = rootMsg
		self.requestMsg = requestMsg
		self.msgType = msgType
		self.timeRec = timeRec
		self.messageProcessor = MessageProcessor()

	def run(self):
		# logMe("Started " + self.name)
		self.messageProcessor.processMessage(self.sessionid, self.msisdn, self.rootMsg, self.requestMsg, self.msgType, self.timeRec)

	# print "Exiting " + self.name
	def stop(self):
		# logMe("Trying to stop " + self.name)
		exitFlag = 1
		self.run = False


class EmailMessageProcessorThread(threading.Thread):
	"""docstring for USSDMessageProcessorThread"""

	def __init__(self, email_subject, body_of_email, recipient):
		threading.Thread.__init__(self)
		self.email_subject = email_subject
		self.body_of_email = body_of_email
		self.recipient = recipient
		self.emailservice = EmailService()

	def run(self):
		# logMe("Started " + self.name)
		self.emailservice.sendMessage(self.email_subject, self.body_of_email, self.recipient)

	# print "Exiting " + self.name
	def stop(self):
		# logMe("Trying to stop " + self.name)
		exitFlag = 1
		self.run = False

def processMessage(sessionId, msisdn, rootMsg, requestMsg, msgType, ranNow):
	#lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
	session = recordMessage(sessionId, msisdn, rootMsg, requestMsg, msgType ,'',"1")
	try:
		banned = client.get_api("varmani.isBanned","msisdn=" + msisdn)
	except:
		banned = False

	#currentTime = datetime.datetime.now()
	#diffTime = currentTime - lastTimeCheck
	#secondsTime = diffTime.total_seconds()
	#print 'checking banned'
	# print session
	message_type = 'USER_REQUEST'
	if (banned != True or banned==None):
		#print 'NOT banned'
		try:
			customer = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.get_customer","msisdn=" + msisdn) #returns varmani network node
			if customer <> None:
				# if speed dial
				# print 'stored command: ' + session['command']
				# print customer['name']
				req_msg=requestMsg.split('*130*826')
				# print req_msg
				# print req_msg[len(req_msg)-1]
				if rootMsg != '*130*826#':#Speed dials
					options = requestMsg.split('*')
					print str(options)
					if options[0] == '0': #Buy products
						pass
					elif options[0] == '1':#Refer - *ID*SERIALNUMBER
						try:
							id = options[1]
							# print id
						except:
							id = None
							message = 'ID Number not provided or invalid'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'ERROR'
						try:
							serial_number = options[2]
							# print serial_number
						except:
							serial_number = None
							message = 'ID Number not provided or invalid'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'ERROR'
						if id!= None and serial_number!=None:
							# print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
							result = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.referral", "id=%s&serial=%s&referrer=%s" % (options[1],options[2],customer['name']))
							message = result['message']
							message_type = result['message_type']
							next_command = result['next_command']

					elif options[0] == '01':  # Opt in - *ID
						try:
							id = options[1]
						# print id
						except:
							id = None
							message = 'ID Number not provided or invalid'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'ERROR'

						if id != None:
							result = client.get_api(
								"varmani.varmani.doctype.varmani_network.varmani_network.opt_in",
								"id=%s&msisdn=%s" % (
									options[1], msisdn))
							message = result['message']
							message_type = result['message_type']
							next_command = result['next_command']
							customer = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.get_customer",
											  "msisdn=" + msisdn)  # returns varmani network node
							print customer
					elif options[0] == '2':#Get a new sim
						try:
							requester = options[1]
						# print id
						except:
							requester = None
							message = 'Sim Number not provided or invalid'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'ERROR'
						if requester != None:
							# print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
							result = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.new_sim",
													"requester=%s&serial=%s" % (
														customer['name'],options[1]))
							message = result['message']
							message_type = result['message_type']
							next_command = result['next_command']

					elif options[0] == '202':  # new sim
						print str(options[1])
						result = client.get_api(
							"varmani.varmani.doctype.varmani_network.varmani_network.is_this_a_varmani_sim",
							"serial_no=%s" % (str(options[1])))
						print str(result)
						if result==None:
							message="You have not provided a Varmani Sim."
						else:
							result = client.get_api(
								"varmani.varmani.doctype.varmani_network.varmani_network.is_this_sim_sold",
								"serial_no=%s" % (str(options[1])))
							print str(result)
							if result == None:
								message = 'Sim is available'
							else:
								message = 'Sim already sold'
						message_type = 'PULL_REQ_CONFIRM'
						next_command = 'INTERNAL'

					elif options[0] == '3':#Balance
						debt = client.get_api("erpnext.accounts.utils.get_balance_on",
											  "party_type=Customer&party=" + customer[
												  "customer"])  # +"&account=Debtors - VAR")
						message = 'Your balance is ' + str(debt * -1)
						message_type = 'PULL_REQ_CONFIRM'
						next_command = 'BALANCE'
					elif options[0] == '33':
						pass
					elif options[0] == '4':# Reset Pin
						pass
					elif options[0] == '111': #Sell a new sim to a Varmani Customer
						pass
					elif options[0] == '99':#Special option for internal use only
						pass
					elif options[0] == '911':#Helpdesk request by Varmani Customer
						pass
					else:
						message = 'Unknown request: ' + requestMsg
						message_type = 'PULL_REQ_CONFIRM'
						next_command = 'ERROR'
				else:
					if session['command'] == '':
						debt = client.get_api("erpnext.accounts.utils.get_balance_on",
											  "party_type=Customer&party=" + customer[
												  "customer"])  # +"&account=Debtors - VAR")
						message = 'Welcome ' + customer["full_name"] + ', please provide your pin.'
						message_type = 'USER_REQUEST'
						next_command = 'PIN'
					if session['command']=='PIN':
				# print 'msisdn="%s"&pin="%s"' %(msisdn, requestMsg)
						pin_verified = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.verify_varmani_customer_pin", 'msisdn=%s&pin=%s' %(msisdn, requestMsg))
						# print pin_verified
						if pin_verified==True:
							message = 'Menu\n0- Buy a Varmani Product\n1- Refer Others\n2- Add a new sim to your account\n3- My Account Balance\n4- Reset your pin\nNeed Help? Dial *130*826*911#'
							message_type = 'USER_REQUEST'
							next_command = 'BUY'
						else:
							message = 'Pin NOT verify, please try again.'
							message_type = 'USER_REQUEST'
							next_command = 'PIN'

					elif session['command']== 'BUY':
						if requestMsg == '0': #buy product
							message = 'Which product would you like to buy\n1) Airtime\n2) Electricity (Coming Soon)\nNeed Help? Dial *130*826*911#'
							message_type = 'USER_REQUEST'
							next_command = 'BUY'
						elif requestMsg == '1': #refer
							message = 'You are buying\n Airtime\nNeed Help? Dial *130*826*911#'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'SELECT'
						elif requestMsg == '2': #new sim
							message = 'You are buying\n Electricity (Coming Soon)\nNeed Help? Dial *130*826*911#'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'SELECT'
						elif requestMsg == '3': #balance
							debt = client.get_api("erpnext.accounts.utils.get_balance_on",
												  "party_type=Customer&party=" + customer[
													  "customer"])  # +"&account=Debtors - VAR")
							message = 'Your balance is ' + str(debt * -1)
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'MENU'
						elif requestMsg == '4':#reset pin
							pass
						elif requestMsg == '99': #only for varmani
							pass
					elif session['command']== 'ID_TYPE':
						pass
					elif session['command']== 'ID_NUMBER':
						pass
					elif session['command']== 'SIMNUM':
						pass
					elif session['command']== 'SELECT':
						pass
					elif session['command']== 'SENDTO':
						pass
					elif session['command']== 'LOADTO':
						pass
					elif session['command']== ' AMOUNT':
						pass
					elif session['command']== 'CONFIRM_VEND':
						message_type = 'PULL_REQ_CONFIRM'
					#print customer
					#print customer["full_name"]

					# print message
					# print message_type
					# print next_command

				print message
				print message_type
				print next_command

				sendUSSD(sessionId,msisdn,message,message_type)#'USER_REQUEST')PULL_REQ_CONFIRM
				recordMessage(sessionId, msisdn, rootMsg, message, message_type, next_command, "0")
			else:
				req_msg = requestMsg.split('*130*826')
				# print req_msg
				# print req_msg[len(req_msg)-1]
				if rootMsg != '*130*826#':  # Speed dials
					options = requestMsg.split('*')
					if options[0] == '01':  # opt in - *ID
						try:
							id = options[1]
						# print id
						except:
							id = None
							message = 'ID Number not provided or invalid'
							message_type = 'PULL_REQ_CONFIRM'
							next_command = 'ERROR'

						if id != None:
							customer = client.get_api(
								"varmani.varmani.doctype.varmani_network.varmani_network.get_customer",
								"id=" + id)  # returns varmani network node
							print customer
							if customer <> None:
								# print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
								result = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.opt_in",
														"id=%s&msisdn=%s" % (
															options[1], msisdn))
								message = result['message']
								message_type = result['message_type']
								next_command = result['next_command']

								sendUSSD(sessionId, msisdn, message, message_type)  # 'USER_REQUEST')PULL_REQ_CONFIRM
								recordMessage(sessionId, msisdn, rootMsg, message, message_type, next_command, "0")
							else:
								print 'No customer with msisdn=' + msisdn + ' found.'
								recordMessage(sessionId, msisdn, rootMsg, 'No customer with msisdn=' + msisdn + ' found.',
											  msgType, '', "0")
						else:
							print 'No customer with msisdn=' +msisdn + ' found.'
							recordMessage(sessionId, msisdn, rootMsg, 'No customer with msisdn=' +msisdn + ' found.', msgType, '', "0")
		except:
			#sendUSSD(sessionId,msisdn,'Not Authorised!','PULL_REQ_CONFIRM')
			print(sys.exc_info()[0] )
			recordMessage(sessionId, msisdn, rootMsg, 'Not Authorised!', msgType, '', "0")


		#localtime = time.asctime(time.localtime(time.time()))
		#current = datetime.datetime.now().replace(microsecond=0)
		#diff = current - ranNow
		#seconds = diff.total_seconds()
		#lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
		seconds = 0

		#currentTime = datetime.datetime.now()
		#diffTime = currentTime - lastTimeCheck
		#secondsTime = diffTime.total_seconds()
		#print 'sending message',secondsTime

		#lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

		#currentTime = datetime.datetime.now()
		#diffTime = currentTime - lastTimeCheck
		#secondsTime = diffTime.total_seconds()
		#print 'Storing sessiong message', secondsTime
	else:
		#sendUSSD(sessionId,msisdn,'Not Authorised!','PULL_REQ_CONFIRM')
		recordMessage(sessionId, msisdn, rootMsg, 'Banned!', msgType, '', "0")


def recordMessage(sessionid, msisdn, rootMsg, requestMsg, msgType, last_command, direction):

	#self.client = FrappeClient("https://www.varmani.co.za","administrator","gauranga")
	# print last_command
	try:
		nameMSISDN = client.get_value("MSISDN Communications", "name", {"msisdn": msisdn})
		if nameMSISDN:
			docMSISDN = client.get_doc("MSISDN Communications", nameMSISDN["name"])
		else:
			docMSISDN = {"doctype": "MSISDN Communications"}

		name = client.get_value("USSD Session", "name", {"ussd_sessionid": sessionid})
		if name:
			doc = client.get_doc("USSD Session", name["name"])
			#oldmessages = doc["messages"]
			doc["messages"] += "|- %s -|- %s -|- %s -|- %s -|- %s -|\n" % (datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), direction, msisdn, msgType, requestMsg)
			#doc["messages"] = oldmessages
			if last_command != '':
				doc['command'] = last_command
		else:
			doc = {"doctype":"USSD Session"}
			doc['command'] = ''
			doc["messages"] = "|- %s -|- %s -|- %s -|- %s -|- %s -|\n" % (datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), direction, msisdn, msgType, requestMsg)


		docMSISDN["msisdn"] = msisdn
		doc["ussd_sessionid"] = sessionid
		doc["msisdn"] = msisdn
		doc["root_message"] = rootMsg
		localtime = datetime.datetime.now().replace(microsecond=0)
		doc["date"] = localtime.strftime("%Y-%m-%d %H:%M:%S")

		#mdoc = {"doctype":"USSD Message"}
		#mdoc["incoming"] = direction
		#mdoc["msisdn"] = msisdn
		#mdoc["message"] = requestMsg
		#mdoc["message_type"]=msgType
		#oldmessages = doc["messages"]
		#doc["messages"] = "|%s|%s|%s|%s|\n" % (direction, msisdn, requestMsg, msgType)
		# = oldmessages

		#print doc["messages"]
		#print(doc)

		try:
			docMSISDN['ussd_sessions'].append(doc)
		except:
			docMSISDN['ussd_sessions'] = []
			docMSISDN['ussd_sessions'].append(doc)

		#print(docMSISDN)
		#print "this far"
		docMSISDN['session_count'] = client.get_api("varmani.USSDMessageCount", "msisdn=" + msisdn)

		if nameMSISDN:
			client.update(docMSISDN)
		else:
			client.insert(docMSISDN)

		return doc

	except:
		print("something went wrong")
		print(sys.exc_info()[0])

		return None
	#print doc


def sendUSSD(sessionId, msisdn, msg, msgType):
	responseMeg = "<usareq NODE='" + settingObj['ussd_node'] + "' TRANSFORM='USSD' USERNAME='" + settingObj['ussd_username'] + "' PASSWORD='" + settingObj['ussd_password'] + "' VERBOSITY='2'><command><ussd_response><sessionid>"+ sessionId+"</sessionid><type>"+msgType +"</type><msisdn>"+ msisdn+"</msisdn><message>"+ msg+"</message></ussd_response></command></usareq>"
	r = requests.post(settingObj['message_url'], data = {'command':responseMeg} )

def getLoginMessage():
	return "<usereq USERNAME='"+settingObj['ussd_username']+"' PASSWORD='"+ settingObj['ussd_password']+"' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='\*'/></usereq>END"


def USSDClient(messenger):
	# if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(1)

	# connect to remote host
	try:
		s.connect((messenger.getUSSDSocketIP(), messenger.getUSSDSocketPort()))
	except Exception as e:
		#print(sys.exc_info()[0])
		logMe('Unable to connect: ' + str(e))
	# sys.exit()

	logMe('Connected to remote host. Start sending messages')
	loginMessage = getLoginMessage()
	# print loginMessage

	s.send(loginMessage)

	##prompt()

	while not exitFlag:
		# print "running...."

		socket_list = [s]
		#        time.sleep(30)
		#        break
		# Get the list sockets which are readable
		# print "Listerning"
		read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [], 1)
		# print "after stop"
		for sock in read_sockets:
			# print "incoming message from remote server"
			if sock == s:
				data = sock.recv(4096)
				if not data:
					logMe('\nDisconnected from chat server')
					time.sleep(100)
					break
				else:
					# print data
				#try:
					root = ET.fromstring(data)
					for datablock in root.findall('datablock'):
						lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
						sessionid = datablock.find('sessionid').text
						msisdn = datablock.find('msisdn').text
						rootMsg = datablock.find('svcCode').text
						requestMsg = datablock.find('message').text.replace('*130*826*', '').replace('#', '')
						msgType = datablock.find('type').text
						localtime = time.asctime(time.localtime(time.time()))
						ranNow = datetime.datetime.now().replace(microsecond=0)
						saveTime = "timeRec=" + ranNow.strftime("%Y-%m-%d %H:%M:%S")
						logMe(localtime + " | " + sessionid + " | " + msisdn + " | " + rootMsg + " | " + requestMsg + " | " + msgType + " | " + saveTime)
						#currentTime = datetime.datetime.now()
						#diffTime = currentTime - lastTimeCheck
						#secondsTime = diffTime.total_seconds()
						#print "pasing message before processing", secondsTime

						lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
						processMessage(sessionid, msisdn, rootMsg, requestMsg, msgType, ranNow)
						#ussdProc = USSDMessageProcessorThread(sessionid, msisdn, rootMsg, requestMsg, msgType, ranNow)
						#ussdProc.daemon = True
						#ussdProc.start()
						#currentTime = datetime.datetime.now()
						#diffTime = currentTime - lastTimeCheck
						#secondsTime = diffTime.total_seconds()
						#print 'thread ussdprocess', secondsTime

						# messenger.sendUSSD(sessionid, msisdn, localtime + ' - ' + requestMsg, 'USER_REQUEST' )
						try:
							# print "logging in...."
							#client = FrappeClient(aD['url'], aD['username'], aD['password'])
							lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
							client.post_api("varmani.setLastTime", saveTime)

							#currentTime = datetime.datetime.now()
							#diffTime = currentTime - lastTimeCheck
							#secondsTime = diffTime.total_seconds()
							#print 'storing time communication',secondsTime
						except Exception as e:
							#print(sys.exc_info()[0])
							logMe("Unexpected error:" + str(e))
						# prompt()
					#except:
					#	pass

			# user entered a message
			else:
				msg = sys.stdin.readline()
			# prompt()

lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
count=0
while 1:
	try:
		client = FrappeClient(aD['url'], aD['username'], aD['password'])
		settingObj = client.get_api("varmani.getMTNServiceSettings")
		# print settingObj['rica_password']
		break
	except:
		time.sleep(10)
		count=count + 1
		if count >=10:
			break

#currentTime = datetime.datetime.now()
#diffTime = currentTime - lastTimeCheck
#secondsTime = diffTime.total_seconds()
#print 'started and created client', secondsTime

lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

#client = FrappeClient(aD['url'], aD['username'], aD['password'])
threadUSSD = USSDListernerThread("1")
threadUSSD.daemon = True
threadUSSD.start()

#currentTime = datetime.datetime.now()
#diffTime = currentTime - lastTimeCheck
#secondsTime = diffTime.total_seconds()
#print 'created the ussd thread',secondsTime

myMessenger = EmailService()  # MessageSerice()
mySMSer = MessageSerice()
localtime = time.asctime(time.localtime(time.time()))
myMessenger.sendMessage("USSD Service started", "USSD Service started on " + localtime, "hem@varmani.co.za")
mySMSer.sendSMS('27810378419',"USSD Service started on " + localtime)
errorCount = 0

storedTime = client.get_api("varmani.getLastTime")
lastCheck = datetime.datetime.strptime(storedTime, "%Y-%m-%d %H:%M:%S")
while 1:
	try:
		current = datetime.datetime.now().replace(microsecond=0)
		diff = current - lastCheck
		minutes = diff.total_seconds() / 60
		#print minutes
		if minutes >= 30:
			lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

			#client = FrappeClient(aD['url'], aD['username'], aD['password'])
			storedTime = client.get_api("varmani.getLastTime")
			# print storedTime
			lastCheck = datetime.datetime.strptime(storedTime, "%Y-%m-%d %H:%M:%S")
			current = datetime.datetime.now().replace(microsecond=0)
			diff = current - lastCheck
			minutes = diff.total_seconds() / 60
			# print minutes
			if minutes >= 30:
				exitFlag = 1
				# print "Exiting threads"
				threadUSSD.join()
				# threadUSSD.start()
				try:
					# print "logging in...."
					#client = FrappeClient(aD['url'], aD['username'], aD['password'])
					client.post_api("varmani.setLastTime", "timeRec=" + current.strftime("%Y-%m-%d %H:%M:%S"))
					lastCheck = current
				# localtime = time.asctime(time.localtime(time.time()))
				# sendSMS('27810378419', "USSD Service restarted on " + localtime)
				except Exception as e:
					logMe("Unexpected error: " + str(e))

				logMe("Trying to restart thread")
				exitFlag = 0
				threadUSSD = USSDListernerThread("1")
				threadUSSD.daemon = True
				threadUSSD.start()
			#currentTime = datetime.datetime.now()
			#diffTime = currentTime - lastTimeCheck
			#secondsTime = diffTime.total_seconds()
			#print 'restarting the ussd thread', secondsTime

	except KeyboardInterrupt:
		logMe("keyboard interupt")
		break
	except Exception as ee:
		logMe("Unexpected error: " + str(ee))
		errorCount = errorCount + 1
		time.sleep(10)
		if errorCount > 10:
			break

# Notify threads it's time to exit
exitFlag = 1

logMe('Waiting for worker threads')
main_thread = threading.currentThread()
for t in threading.enumerate():
	# logMe(t.name)
	if t is not main_thread:
		t.join()

# Wait for all threads to complete
logMe("Exiting Main Thread")
myMessenger.sendMessage("USSD Service STOPPED", "USSD Service STOPPED on " + localtime, "hem@varmani.co.za")
mySMSer.sendSMS('27810378419',"USSD Service STOPPED on " + localtime)