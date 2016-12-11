import frappe
from scripts import messageService
from erpnext.stock.utils import get_stock_balance
import datetime
from frappe.utils.password import get_decrypted_password
from frappe.utils import cint
import sys

__version__ = '0.0.2'

@frappe.whitelist(allow_guest=False)
def getMTNServiceSettings():
	data =frappe.get_doc("MTN Services Settings")
	data.ussd_password = get_decrypted_password('MTN Services Settings', 'MTN Services Settings', 'ussd_password', False)
	data.sms_password = get_decrypted_password('MTN Services Settings', 'MTN Services Settings', 'sms_password', False)
	data.rica_password = get_decrypted_password('MTN Services Settings', 'MTN Services Settings', 'rica_password', False)
	return data

@frappe.whitelist(allow_guest=False)
def getCommissionAccountSettings():
	data =frappe.get_doc("Network Account Settings")
	return data

@frappe.whitelist(allow_guest=False)
def setLastTime(timeRec):
	data = frappe.db.set_value("MTN Services Settings", None, "last_message_received_on", timeRec)
	return data
	
@frappe.whitelist(allow_guest=False)
def getLastTime():
	data =frappe.get_doc("MTN Services Settings")
	return data.last_message_received_on

@frappe.whitelist(allow_guest=False)
def isBanned(msisdn):
	try:
		data = frappe.get_doc("MSISDN Communications", {'msisdn': msisdn})
		return data.banned#['message']#['banned']#True
		#data = frappe.get_doc("Banned MSISDN", {'msisdn': msisdn})
		#return data#True
	except:
		return None


@frappe.whitelist(allow_guest=True)
def sendSMS(msisdn, message, username, psd):
	name = frappe.get_value("SMS Customer",{'user_name':username, 'password':psd},'name')
	if name:
		smsCustomer = frappe.get_doc("SMS Customer",name)
		if smsCustomer.active:
			myMessenger = messageService.MessageSerice()
			response = myMessenger.sendSMS(msisdn, message)
			return response.status_code
		else:
			return None
	else:
		return None

@frappe.whitelist(allow_guest=True)
def ping(whoami):
	return "pong " + whoami

@frappe.whitelist(allow_guest=False)
def update_series(series, current_value):
	if series:
		prefix = series.split('.')[0]
		if not frappe.db.exists('Series', series):
			frappe.db.sql("insert into tabSeries (name, current) values (%s, 0)", (series))

		frappe.db.sql("update `tabSeries` set current = %s where name = %s",
			(current_value, prefix))
		return True #(_("Series Updated Successfully"))
	else:
		return False #msgprint(_("Please select prefix first"))


@frappe.whitelist(allow_guest=False)
def USSDMessageCount(msisdn):
	#return msisdn
	count = frappe.db.sql("""select count(*) from `tabUSSD Session` where msisdn=%s""", msisdn)[0][0]
	return count


@frappe.whitelist(allow_guest=False)
def GetInvoice(invoice, qty, itemcode, amount):
	if invoice == 'Sales':
		data = frappe.db.sql("""select name, parent, idx from `tabSales Invoice Item` where qty=%s and item_code=%s""", (qty,itemcode))
	elif invoice == 'Purchase Credit':
		data = frappe.db.sql(
			"""select name, parent, idx from `tabPurchase Invoice Item` where qty=%s and item_name=%s and amount=%s""",
			(qty, itemcode,amount))
	else:
		data = frappe.db.sql(
			"""select name, parent, idx from `tabPurchase Invoice Item` where qty=%s and item_code=%s""",
			(qty, itemcode))
	return data

