# telnet program example
import socket, select, string, sys
import xml.etree.ElementTree as ET
import requests, logging
import time, threading, datetime
from frappeclient import FrappeClient
import json

class MessageSerice(object):
	def __init__(self):
		accessDetails = open('/home/hemant/access.txt')
		aD = json.loads(accessDetails.read())
		#print client
		self.client = FrappeClient(aD['url'],aD['username'],aD['password'])
		#FrappeClient(aD['url'],aD['username'],aD['password'])
		self.settingObj = self.client.get_api("varmani.getMTNServiceSettings")

	def logMe(self, msg):
		localtime = datetime.datetime.now().replace(microsecond=0)
		message = "[" + localtime.strftime("%Y-%m-%d %H:%M:%S") + "] " + msg + "\r\n"
		sys.stdout.write(message)
		sys.stdout.flush()

	def sendSMS(self, msisdn, msg):
		responseMeg = "<usareq NODE='" + self.settingObj['sms_node'] + "' TRANSFORM='SUBMIT_SM' USERNAME='" + self.settingObj['sms_username'] + "' PASSWORD='" + self.settingObj['sms_password'] + "'><command><submit_sm><a_number>" + self.settingObj['sms_a_number'] + "</a_number><b_number>" + msisdn + "</b_number><service_type></service_type><message>"+ msg +"</message><registered_delivery></registered_delivery></submit_sm></command></usareq>"
		self.logMe("sms sent: " + msg + " to " + msisdn)
		r = requests.post(self.settingObj['message_url'], data = {'command': responseMeg} )
		return r

	def sendUSSD(self, sessionId, msisdn, msg, msgType):
		responseMeg = "<usareq NODE='" + self.settingObj['ussd_node'] + "' TRANSFORM='USSD' USERNAME='" + self.settingObj['ussd_username'] + "' PASSWORD='" + self.settingObj['ussd_password'] + "' VERBOSITY='2'><command><ussd_response><sessionid>"+ sessionId+"</sessionid><type>"+msgType +"</type><msisdn>"+ msisdn+"</msisdn><message>"+ msg+"</message></ussd_response></command></usareq>"
		r = requests.post(self.settingObj['message_url'], data = {'command':responseMeg} )
		
 
	def getUSSDUsername(self):
		return self.settingObj['ussd_username']

	def getUSSDPassword(self):
		return self.settingObj['ussd_password']

	def getUSSDSocketIP(self):
		return self.settingObj['ussd_server_socket_ip']
		
	def getUSSDSocketPort(self):
		return int(self.settingObj['ussd_server_socket_port'])
		
	def getLoginMessage(self):
		return "<usereq USERNAME='"+self.settingObj['ussd_username']+"' PASSWORD='"+self.settingObj['ussd_password']+"' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='\*'/></usereq>END"
