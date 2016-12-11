# telnet program example
import socket, select, string, sys
import xml.etree.ElementTree as ET
import requests, logging
import time, threading, datetime
from Queue import Queue
from varmani.scripts.frappeclient import FrappeClient
import json
from varmani.scripts.messageService import MessageSerice as myService


class MessageProcessor(object):
	def __init__(self):
		accessDetails = open('/home/hemant/access.txt')
		aD = json.loads(accessDetails.read())
		lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
		self.client = FrappeClient(aD['url'],aD['username'],aD['password'])
		currentTime = datetime.datetime.now()
		diffTime = currentTime - lastTimeCheck
		secondsTime = diffTime.total_seconds()
		#print 'USSD Processor login', secondsTime

		lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
		self.settingsObj = self.client.get_api("varmani.getMTNServiceSettings")
		currentTime = datetime.datetime.now()
		diffTime = currentTime - lastTimeCheck
		secondsTime = diffTime.total_seconds()
		#print 'Getting settings', secondsTime

		lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
		self.myMessageService = myService()
		currentTime = datetime.datetime.now()
		diffTime = currentTime - lastTimeCheck
		secondsTime = diffTime.total_seconds()
		#print 'init message service', secondsTime

		
	def logMe(self, msg):
		#localtime = datetime.datetime.now().replace(microsecond=0)
		#message = "[" + localtime.strftime("%Y-%m-%d %H:%M:%S") + "] " + msg + "\r\n"
		#sys.stdout.write(message)
		#sys.stdout.flush()
		pass

	def processMessage(self, sessionId, msisdn, rootMsg, requestMsg, msgType, ranNow):
		localtime = time.asctime(time.localtime(time.time()))
		current = datetime.datetime.now().replace(microsecond=0)
		diff = current - ranNow
		seconds = diff.total_seconds()

		lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
		banned = self.client.get_api("varmani.isBanned","msisdn=" + msisdn)
		currentTime = datetime.datetime.now()
		diffTime = currentTime - lastTimeCheck
		secondsTime = diffTime.total_seconds()
		#print 'checking banned', secondsTime
		#print banned
		if (banned != True or banned==None):
			lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
			self.myMessageService.sendUSSD(sessionId,msisdn,str(seconds) + ' - ' + requestMsg,'USER_REQUEST')

			currentTime = datetime.datetime.now()
			diffTime = currentTime - lastTimeCheck
			secondsTime = diffTime.total_seconds()
			#print 'sending message',secondsTime

			lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
			self.recordMessage(sessionId, msisdn, rootMsg, requestMsg, msgType)
			currentTime = datetime.datetime.now()
			diffTime = currentTime - lastTimeCheck
			secondsTime = diffTime.total_seconds()
			#print 'Storing sessiong message', secondsTime
	
	def recordMessage(self, sessionid, msisdn, rootMsg, requestMsg, msgType):
		#self.client = FrappeClient("https://www.varmani.co.za","administrator","gauranga")
		name = self.client.get_value("USSD Session", "name", {"sessionid": sessionid})
		
		if name:
			doc = self.client.get_doc("USSD Session", name["name"])
		else:
			doc = {"doctype":"USSD Session"}
			
		doc["sessionid"] = sessionid
		doc["msisdn"] = msisdn
		doc["root_message"] = rootMsg
		localtime = datetime.datetime.now().replace(microsecond=0)
		doc["date"] = localtime.strftime("%Y-%m-%d %H:%M:%S")
		mdoc = {"doctype":"USSD Message"}
		mdoc["incoming"] = "1"
		mdoc["msisdn"] = msisdn
		mdoc["message"] = requestMsg
		mdoc["message_type"]=msgType
		#print doc.messages
		try:
			doc['messages'].append(mdoc)
		except:
			doc['messages']=[]
			doc['messages'].append(mdoc)

		if name:
			self.client.update(doc)
		else:
			self.client.insert(doc)
			
		#print doc
		
		
		
		