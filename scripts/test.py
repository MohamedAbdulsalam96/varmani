import json, time
from emailService import EmailService
from frappeclient import FrappeClient
import socket, select, string, sys
from messageService import MessageSerice

accessDetails = open('/home/hemant/access.txt')
aD = json.loads(accessDetails.read())

#print aD
#print aD['username']
#myMessenger = EmailService()
#localtime = time.asctime(time.localtime(time.time()))
#myMessenger.sendMessage("USSD Service started", "USSD Service started on " + localtime, "hem@varmani.co.za")

#try:
msisdn = '27810378419'
client = FrappeClient(aD['url'], aD['username'], aD['password'])
customer = client.get_api("varmani.get_customer","msisdn=" + msisdn)
if customer not None:
	print (customer)
	print (customer["full_name"])
	debt = client.get_api("erpnext.accounts.utils.get_balance_on","party_type=Customer&party=" + customer["customer"] +"&account=Debtors - VAR")
	print ('Welcome ' + customer["full_name"] + ' (' + str(debt*-1) + ')')
	result = client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.referral",
							"id=%s&serial=%s&referrer=%s" % ('6506040495087', '1733452431', customer['name']))

	new_varmani_network = {"doctype":'Varmani Network'}
	new_varmani_network["parent_varmani_network"] = customer['name']
	new_varmani_network["old_parent"] = customer['name']
	new_varmani_network["identity_number"] = '6506040495087'
	print (new_varmani_network)
	client.insert(new_varmani_network)
	print (result)
else:
	print ('No customer with msisdn=' +msisdn + ' found.')
#except:
	#sendUSSD(sessionId,msisdn,'Not Authorised!','PULL_REQ_CONFIRM')
#	print(sys.exc_info()[0] )

#myMessenger = EmailService()
localtime = time.asctime(time.localtime(time.time()))
#myMessenger.sendMessage("USSD Service started", "USSD Service started on " + localtime, "hem@varmani.co.za")

# mySmsMessanger = MessageSerice()
# mySmsMessanger.sendSMS(msisdn, 'service started')

