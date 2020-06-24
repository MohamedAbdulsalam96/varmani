# -*- coding: utf-8 -*-
# Copyright (c) 2015, Hemant Pema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint
from frappe import throw, _
from frappe.utils.password import get_decrypted_password
import requests, sys

class RootNotEditable(frappe.ValidationError): pass

class VarmaniNetwork(Document):
	nsm_parent_field = 'parent_varmani_network'

	def update_nsm_model(self):
		"""update lft, rgt indices for nested set model"""
		import frappe
		import frappe.utils.nestedset
		frappe.utils.nestedset.update_nsm(self)

	def on_update(self):
		self.update_nsm_model()

	def on_trash(self):
		self.update_nsm_model()

	def validate(self):
		try:
			if self.ref_full_name == None and self.parent_varmani_network != '':
				referer = frappe.get_doc("Varmani Network", self.parent_varmani_network)
				r_customer = frappe.get_doc("Customer", referer.customer)
				self.ref_full_name = r_customer.customer_name
				frappe.msgprint(_(r_customer))

			if self.get('__islocal'):
				# frappe.msgprint(_(self.customer))
				# frappe.msgprint(_(self.full_name))
				if not self.full_name or self.full_name != self.customer:
					if self.customer != None or self.customer !='':
						customer = frappe.get_doc("Customer",self.customer)
						self.full_name=customer.customer_name

				if self.identity_number == '' or self.identity_number == None:
					if self.customer != None or self.customer != '':
						customer = frappe.get_doc("Customer", self.customer)
						self.identity_number = customer.identity_number

			# frappe.msgprint(_(referer.customer))
			# frappe.msgprint(str(self.identity_number))

		except:
			pass




@frappe.whitelist(allow_guest=True)
def referral(id,referrer,serial='',customer_fullname='', customer_msisdn='', pin='', via_ussd=True):
	if via_ussd==True:
		if is_this_a_varmani_sim(serial):
			if is_this_sim_sold(serial):
				return  {
				'message' : 'Sim already used for another customer, please use a new Varmani Sim to refer other customers.',
				'message_type': 'PULL_REQ_CONFIRM',
				'next_command' : 'ERROR'
			}
			else:
				exists = is_this_customer_refered(id)
				if exists:
					if exists.full_name != None:
						return {
							'message': exists.full_name + ' already referred by ' + exists.ref_full_name + ' therefore cannot be referred by you.',
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'ERROR'
						}
					else:
						return {
							'message': exists.identity_number+ ' already referred by ' + exists.ref_full_name + ' therefore cannot be referred by you.',
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'ERROR'
						}
				else:
					if validate_id(id):
						new_varmani_network = frappe.new_doc('Varmani Network')
						#new_varmani_network.customer = id
						new_varmani_network.parent_varmani_network = referrer
						new_varmani_network.old_parent = referrer
						new_varmani_network.identity_number = id
						new_varmani_network.insert()

						new_rica = frappe.new_doc('RICA Submission')
						new_rica.customer = new_varmani_network.name
						sim = frappe.new_doc('Sims To Rica')
						sim.serial_no = serial
						new_rica.append('sims_to_rica',sim)
						new_rica.insert()

						frappe.db.commit()
						#print new_customer.name
						print (new_varmani_network.name)
						return {
							'message': id + ' referred and linked.',
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'REFERRED'
						}
					else:
						return {
							'message': 'ID Number:%s provide is not valid, please check the number and try again.' % id,
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'ERROR'
						}
		else:
			return {
				'message' : 'You have not used a Varmani Sim, please use a Varmani Sim to refer other customers.',
				'message_type': 'PULL_REQ_CONFIRM',
				'next_command' : 'ERROR'
			}
	else:
		exists = is_this_customer_refered(id)
		if exists:
			if exists.full_name != None:
				return {
					'message': exists.full_name + ' already referred by ' + exists.ref_full_name + ' therefore cannot be referred by you.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'ERROR'
				}
			else:
				return {
					'message': exists.identity_number + ' already referred by ' + exists.ref_full_name + ' therefore cannot be referred by you.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'ERROR'
				}
		else:
			if validate_id(id):
				exists = frappe.db.exists('Varmani Network',{'identity_number': referrer})
				if exists:
					referrer = frappe.get_doc('Varmani Network', exists)
					if pin==get_decrypted_password('Varmani Network', referrer.name, 'pin', False):
						if not frappe.db.exists('Customer',{'fullname':customer_fullname}):
							new_customer = frappe.new_doc('Customer')
							new_customer.customer_type = 'Individual'
							new_customer.customer_name = customer_fullname
							new_customer.territory = 'South Africa'
							new_customer.customer_group = 'Individual'
							new_customer.insert(ignore_permissions=True)
						else:
							new_customer = frappe.get_doc('Customer', customer_fullname)

						new_varmani_network = frappe.new_doc('Varmani Network')
						new_varmani_network.customer = new_customer.name
						new_varmani_network.parent_varmani_network = referrer.name
						new_varmani_network.old_parent = referrer.name
						new_varmani_network.identity_number = id
						new_varmani_network.msisdn = customer_msisdn
						new_varmani_network.insert(ignore_permissions=True)

						new_rica = frappe.new_doc('RICA Submission')
						new_rica.customer = new_varmani_network.name
						fullnames = customer_fullname.split(' ')
						new_rica.first_names = customer_fullname[0:len(fullnames[0])]
						new_rica.last_names = customer_fullname[len(fullnames[0])+1:]

						#sim = frappe.new_doc('Sims To Rica')
						#sim.serial_no = serial
						#new_rica.append('sims_to_rica', sim)
						new_rica.insert(ignore_permissions=True)
						try:
							sendSMS(new_varmani_network.msisdn,
								'Hello ' + customer_fullname + ', you have been refered to join NewCo. Please dial *130*826*01*' + id + ' to confirm.')
						except:
							pass

						frappe.db.commit()
						# print new_customer.name
						# print new_varmani_network.name
						return {
							'message': 'Customer: ' + new_customer.name + ' with ID: ' + id + ' has been referred and linked to you.',
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'REFERRED'
						}
					else:
						return {
							'message': 'You have entered an incorrect pin',
							'message_type': 'PULL_REQ_CONFIRM',
							'next_command': 'ERROR'
						}
				else:
					return {
						'message': 'You are not a valid customer of NewCo so you cannot refer customers',
						'message_type': 'PULL_REQ_CONFIRM',
						'next_command': 'ERROR'
					}
			else:
				return {
					'message': 'ID Number:%s provide is not valid, please check the number and try again.' % id,
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'ERROR'
				}


@frappe.whitelist(allow_guest=False)
def new_sim(requester,serial):
	customer = frappe.get_doc('Varmani Network', requester)
	if is_this_a_varmani_sim(serial):
		if is_this_sim_sold(serial):
			return  {
			'message' : 'Sim already used for another customer, please use a new Varmani Sim to refer other customers.',
			'message_type': 'PULL_REQ_CONFIRM',
			'next_command' : 'ERROR'
		}
		else:
			if frappe.db.exists('RICA Submission',{'customer':customer.name}):
				rica = frappe.get_doc('RICA Submission', frappe.get_value('RICA Submission',{'customer':customer.name},'name'))
				sim = frappe.new_doc('Sims To Rica')
				sim.serial_no = serial
				rica.append('sims_to_rica',sim)
				rica.save()

				frappe.db.commit()
				#print new_customer.name

				return {
					'message': serial + ' has been added to your name and submitted for RICA. You will be inform when that is completed then you can activate the sim.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'REFERRED',
					'name':rica.name
				}
			else:
				new_rica = frappe.new_doc('RICA Submission')
				new_rica.customer = customer.name
				sim = frappe.new_doc('Sims To Rica')
				sim.serial_no = serial
				new_rica.append('sims_to_rica', sim)
				new_rica.insert()

				frappe.db.commit()
				# print new_customer.name
				# print new_varmani_network.name
				return {
					'message': id + ' referred and linked.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'REFERRED',
					'name':new_rica.name
				}
	else:
		return {
			'message' : 'You have not used a Varmani Sim, please use a Varmani Sim to refer other customers.',
			'message_type': 'PULL_REQ_CONFIRM',
			'next_command' : 'ERROR'
		}

@frappe.whitelist(allow_guest=False)
def is_this_a_varmani_sim(serial_no):
	exists = frappe.db.exists('Serial No',{'serial_no':serial_no})
	if exists:
		return True
	else:
		return False

@frappe.whitelist(allow_guest=False)
def is_this_sim_sold(serial_no):
	exists = frappe.db.exists('Sims To Rica', {'serial_no': serial_no})
	if exists:
		serial = frappe.get_doc('Serial No', serial_no)
		if serial.customer == None:
			return False
		else:
			return True
	else:
		return False

@frappe.whitelist(allow_guest=False)
def get_customer(msisdn='empty', id=None):
	exists= frappe.db.exists("Varmani Network", {'msisdn': msisdn})
	if exists:
		return frappe.get_doc("Varmani Network", exists)
	else:
		exists = frappe.db.exists("Varmani Network", {'identity_number': id})
		if exists:
			return frappe.get_doc("Varmani Network", exists)
		else:
			return False


def is_this_customer_refered(id):
	exists = frappe.db.exists('Varmani Network',{'identity_number':id})
	if exists:
		return frappe.get_doc('Varmani Network', exists)
	else:
		return exists


@frappe.whitelist(allow_guest=False)
def opt_in(id, msisdn=''):
	#is this a new customer and not using anyone elses msisdn?
	# frappe.msgprint(str(msisdn))
	if msisdn != '':
		exists = frappe.db.exists('Varmani Network', {'msisdn': msisdn})
		if exists:
			varmani_network = frappe.get_doc('Varmani Network', exists)
			if varmani_network.identity_number == id:
				if varmani_network.opt_in==False or varmani_network.opt_in==None:
					varmani_network.opt_in = True
					varmani_network.opted_in_on = frappe.utils.now_datetime()
					varmani_network.save()
					frappe.db.commit()
				return {
					'message': id + ': Hi, you have opted to be part of our revolution. Welcome',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'OPTED',
					'result': True
				}
			else:
				return {
					'message': msisdn + ' belongs to ' + varmani_network.name + ' and cannot be used to opt in others. Please get '+ id +' to opt in with their own sim.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command': 'OPTED',
					"result": False
				}
		else:
			exists = frappe.db.exists('Varmani Network', {'identity_number': id})
			if exists:
				varmani_network = frappe.get_doc('Varmani Network', exists)
				if varmani_network.msisdn == msisdn:
					if not varmani_network.opt_in:
						varmani_network.opt_in = True
						varmani_network.opted_in_on = frappe.utils.now_datetime()
						if varmani_network.msisdn=='' or varmani_network.msisdn==None:
							varmani_network.msisdn = msisdn
						varmani_network.save()
						frappe.db.commit()
					return {
								'message': id + ': Hi, you have opted to be part of our revolution. Welcome',
								'message_type': 'PULL_REQ_CONFIRM',
								'next_command': 'OPTED',
								'result':True
							}
				else:
					return {
						'message': msisdn + ' does not match and cannot be used to opt in. Please get ' + id + ' to opt in with their own sim.',
						'message_type': 'PULL_REQ_CONFIRM',
						'next_command': 'OPTED',
						"result": False
					}
			else:
				return {
					'message': id + ': You cannot opt in if you are not referred to our company, please visit our stores to learn more.',
					'message_type': 'PULL_REQ_CONFIRM',
					'next_command ': 'OPTED',
					"result" : False
				}
	else:
		return {
			'message': 'Cannot opt in customer without msisdn. Please provide the msisdn to contact customer.',
			'message_type': 'PULL_REQ_CONFIRM',
			'next_command': 'OPTED',
			'result':False
		}

def update_party(doc,method):
	#make sure that the commissions account has the party account type and party set so that the balance request is correct
	commission_account = frappe.get_doc('Network Account Settings')
	if doc.account == commission_account.debtors_accrual_account and (doc.party == None or doc.party==''):
		doc.party = doc.against
		doc.party_type = 'Customer'

def is_payment_deleted(doc,method):
	# frappe.msgprint(doc.doctype)
	# if doc.reference_doctype == 'Sales Invoice':
	for r in doc.references:
		# frappe.msgprint(r.name)
		if r.reference_doctype == 'Sales Invoice':
			# frappe.msgprint("""delete from `tabGL Entry` where voucher_type=%s and voucher_no=%s and level!=null""",
			# 			  (r.reference_doctype, r.reference_name))
			frappe.db.sql("""delete from `tabGL Entry` where voucher_type=%s and voucher_no=%s and level>=0""",
						  (r.reference_doctype, r.reference_name))

def is_commission_due(doc, method):
	# frappe.msgprint('incoming data: ' + doc.doctype + ' - ' + method)
	commission_account = frappe.get_doc('Network Account Settings')
	invoice=''
	# frappe.msgprint('against account: ' + str(doc.account))
	if doc.doctype=='Payment Entry':
		invoice_payment= frappe.get_doc('Payment Entry Reference',frappe.get_value('Payment Entry Reference', {'parent': doc.name},'name'))
		invoice = frappe.get_doc('Sales Invoice', invoice_payment.reference_name)
	elif doc.doctype=='GL Entry':
		#frappe.msgprint('accrual:' + commission_account.debtors_accrual_account)
		#frappe.msgprint('expense:' + commission_account.expense_account)
		#frappe.msgprint('credit:' + str(doc.credit))
		#frappe.msgprint('voucher:' + str(doc.against_voucher))
		# frappe.msgprint('Voucher Type: ' + str(doc.against_voucher_type))
		if doc.against_voucher != None and (doc.against!=commission_account.debtors_accrual_account or doc.against!=commission_account.expense_account) and doc.credit !=0 and doc.against_voucher_type=='Sales Invoice':
			#frappe.msgprint(doc.against_voucher)
			invoice = frappe.get_doc('Sales Invoice', doc.against_voucher)
			# frappe.msgprint(invoice.name)

	if invoice!='':
		#frappe.msgprint('invoice:' + invoice.name)
		exists = frappe.db.exists('Varmani Network', {'customer': invoice.customer})
		if exists:
			varmani_customer=frappe.get_doc('Varmani Network',exists)
			# frappe.msgprint('Outstanding Balance: ' + str(invoice.outstanding_amount))
			# for i in payment.deductions:
			if invoice.outstanding_amount==0:
				for l in invoice.items:
					# frappe.msgprint(l.item_code + ' - ' + invoice.name)
					exists=frappe.db.exists('Commission Structure',{'item':l.item_code})
					if exists:
						comm_structure = frappe.get_doc('Commission Structure', exists)

						# comm_journal = frappe.new_doc('GL Entry')
						# comm_journal.naming_series = "JV-"
						# comm_journal.voucher_type = "Journal Entry"
						# comm_journal.cheque_no = invoice.name
						# comm_journal.cheque_date = invoice.posting_date
						# comm_journal.user_remark = 'Commission on invoice: ' + invoice.name
						# comm_journal.docstatus = 1
						# comm_journal.write_off_based_on = "Accounts Receivable"
						# comm_journal.is_opening = "No"
						# comm_journal.posting_date = invoice.posting_date
						# comm_journal.accounts = []

						for c in comm_structure.commission_levels:
							# frappe.msgprint(str(c.level))
							exists=frappe.db.exists('GL Entry',{'account':commission_account.debtors_accrual_account, 'against_voucher':invoice.name, 'level':c.level})
							if not exists:
								if c.level == 0:
									# commission earned for customer
									upline = varmani_customer.name
									if c.is_percentage:
										comm = l.base_net_amount * c.amount / 100
									else:
										comm = l.base_net_amount
								else:
									#commission earned for upline
									upline = get_upline(varmani_customer.name,c.level)
									if upline:
										if c.is_percentage:
											comm = l.base_net_amount*c.amount/100
										else:
											comm = l.base_net_amount

								if upline!='' and comm!=0:
									frappe.msgprint('pay coms on level: ' + str(c.level) + '-' + str(l.item_code) + ' to ' + str(upline) + ' amount of ' + str(comm))

									comm_journal = frappe.new_doc('GL Entry')
									comm_journal.voucher_type = "Sales Invoice"
									comm_journal.voucher_no= invoice.name
									comm_journal.against_voucher = invoice.name
									comm_journal.party_type="Customer"
									comm_journal.debit = 0
									comm_journal.party= upline
									comm_journal.docstatus= 1
									comm_journal.remarks= 'Commission on invoice: ' + invoice.name + ' - level: ' + str(c.level)
									comm_journal.account_currency= "ZAR"
									comm_journal.account = commission_account.debtors_accrual_account
									comm_journal.against_voucher_type = "Sales Invoice"
									comm_journal.against = commission_account.expense_account
									comm_journal.credit = comm
									comm_journal.posting_date = invoice.posting_date
									comm_journal.level = c.level
									comm_journal.insert(ignore_permissions=True)

									# "debit": 33.29,
									# "company": "Varmani Trading Enterprises cc",
									# "debit_in_account_currency": 33.29,
									# "is_advance": "No",
									# "docstatus": 1,
									# "remarks": "No Remarks",
									# "account_currency": "ZAR",
									# "account": "Cash - VAR",
									# "name": "GL1001203",
									# "idx": 0,
									# "modified": "2016-11-05 18:06:23.750676",
									# "against": "hem pem",
									# "credit": 0,
									# "is_opening": "No",
									# "posting_date": "2016-11-05",
									# "credit_in_account_currency": 0

									comm_journal = frappe.new_doc('GL Entry')
									comm_journal.voucher_type = "Sales Invoice"
									comm_journal.voucher_no = invoice.name
									comm_journal.against_voucher = invoice.name
									# comm_journal.party_type = ""
									comm_journal.debit = comm
									comm_journal.docstatus = 1
									comm_journal.remarks = 'Commission on invoice: ' + invoice.name + ' - level: ' + str(c.level)
									comm_journal.account_currency = "ZAR"
									comm_journal.account = commission_account.expense_account
									comm_journal.against_voucher_type = "Sales Invoice"
									comm_journal.against = upline
									comm_journal.credit = 0
									comm_journal.posting_date = invoice.posting_date
									comm_journal.level = c.level
									comm_journal.cost_center = l.cost_center
									comm_journal.insert(ignore_permissions=True)

									# comm_journal.append('accounts', {
									# 	'cost_center': "Main - VAR",
									# 	'party_type': "Customer",
									# 	'reference_type': "Sales Invoice",
									# 	'debit': 0,
									# 	'debit_in_account_currency': 0,
									# 	'credit': comm,
									# 	'credit_in_account_currency': comm,
									# 	'against_account': commission_account.accounts_receivable_account,
									# 	'party': upline,
									# 	'account_type': "Receivable",
									# 	'docstatus':1,
									# 	'account':commission_account.debtors_accrual_account,
									# 	'parenttype':"Journal Entry",
									# 	'parentfield':"accounts",
									# 	'level':c.level
									# })
                                    #
									# comm_journal.append('accounts', {
									# 	'cost_center':"Main - VAR",
									# 	'party_type':"",
									# 	'reference_type':None,
									# 	'debit':comm,
									# 	'debit_in_account_currency':comm,
									# 	'credit':0,
									# 	'credit_in_account_currency':0,
									# 	'against_account':upline,
									# 	'party':"",
									# 	'account_type':"Expense Account",
									# 	'reference_name':None,
									# 	'docstatus':1,
									# 	'account':commission_account.expense_account,
									# 	'parenttype':"Journal Entry",
									# 	'parentfield':"accounts",
									# })

									#frappe.msgprint('inserted-' + str(comm_journal))
						# if len(comm_journal.accounts)>=2:
						# 	comm_journal.insert()



	else:
		# frappe.msgprint('Not and invoice transaction')
		pass



@frappe.whitelist(allow_guest=False)
def get_upline(name,level):
	customer=frappe.get_doc('Varmani Network', name)
	# frappe.msgprint(customer.customer)
	upline_name=name
	for l in xrange(0,int(level)):
		if level ==0:
			upline_name = customer.name
			customer = frappe.get_value('Varmani Network', {'name': upline_name}, 'customer')
		else:
			upline = frappe.get_doc('Varmani Network',upline_name)
			if upline.parent_varmani_network!='':
				# frappe.msgprint(upline.name + ' ' + upline.customer)
				upline_name = upline.parent_varmani_network
				customer = frappe.get_value('Varmani Network',{'name':upline_name},'customer')
			else:
				customer = ''
				break
	return customer


@frappe.whitelist(allow_guest=False)
def verify_varmani_customer_pin(msisdn, pin):
	# print str(pin)
	try:
		data = frappe.get_doc("Varmani Network", {'msisdn': msisdn})
		# return data.name
		password = get_decrypted_password('Varmani Network', data.name, 'pin', False)
		# return password
		if str(password) == str(pin):
			return True
		else:
			return False
	except:
		return 'error' + str(sys.exc_info()[0])


def validate_id(id):
	""" checks to make sure that the card passes a luhn mod-10 checksum """
	sum = 0
	num_digits = len(id)
	oddeven = num_digits & 1

	for count in range(0, num_digits):
		digit = int(id[count])

		if not ((count & 1) ^ oddeven):
			digit = digit * 2
		if digit > 9:
			digit = digit - 9

		sum = sum + digit

	return ((sum % 10) == 0)

def sendSMS(msisdn, msg):
	data = frappe.get_doc("MTN Services Settings")
	data.sms_password = get_decrypted_password('MTN Services Settings', 'MTN Services Settings', 'sms_password', False)

	responseMeg = "<usareq NODE='" + data.sms_node + "' TRANSFORM='SUBMIT_SM' USERNAME='" + data.sms_username + "' PASSWORD='" + data.sms_password + "'><command><submit_sm><a_number>" + data.sms_a_number + "</a_number><b_number>" + msisdn + "</b_number><service_type></service_type><message>"+ msg +"</message><registered_delivery></registered_delivery></submit_sm></command></usareq>"
	r = requests.post(data.message_url, data = {'command': responseMeg} )
	return r
