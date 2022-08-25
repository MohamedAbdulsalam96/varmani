# -*- coding: utf-8 -*-
# Copyright (c) 2015, Hemant Pema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
#from selenium import webdriver
# from selenium.webdriver.common.alert import Alert
# from bs4 import BeautifulSoup
import time, json, sys


class RICASubmission(Document):
	def validate(self):
		self.fullname = " ".join(filter(None, [self.first_names, self.last_names]))
		# rica_sim(self.name)

@frappe.whitelist(allow_guest=False)
def name_verified(first_names,last_names,identity_number, varmani_network, name):
	rica = frappe.get_doc('RICA Submission', name)
	varmani_network = frappe.get_doc('Varmani Network', varmani_network)
	# frappe.msgprint(strreferred(varmani_network.name))
	if varmani_network.customer ==None or varmani_network.customer=='':
		if first_names != '' and last_names != '':
			fullname = " ".join(filter(None, [first_names, last_names]))
			exists = frappe.db.exists('Customer',{'customer_name':fullname})
			if not exists:
				customer = frappe.new_doc('Customer')
				customer.customer_name = fullname
				customer.customer_type = 'Individual'
				if rica.country == '' or rica.country == None:
					customer.territory = 'South Africa'
				else:
					customer.territory = 'Rest Of The World'
				customer.customer_group = 'Individual'
				customer.insert()
			else:
				customer = frappe.get_doc('Customer',frappe.get_value('Customer', {'customer_name':fullname}, 'name'))

			varmani_network.customer=customer.name
			varmani_network.full_name = fullname
			varmani_network.save()
		else:
			frappe.msgprint('First names and last names cannot be empty')
	else:
		pass
		# frappe.msgprint("hmmm")
	# return {
	# 	'fullname':" ".join(filter(None, [first_names, last_names])),
	# 	'ID':identity_number
	# }
	rica.name_verified = True
	rica.name_verified_on = frappe.utils.now_datetime()
	rica.save()
	rica_sim(name)

@frappe.whitelist(allow_guest=False)
def identity_verified(name):
	rica = frappe.get_doc('RICA Submission', name)
	rica.identity_number_verified = True
	rica.identity_number_verified_on = frappe.utils.now_datetime()
	rica.save()
	rica_sim(name)

@frappe.whitelist(allow_guest=False)
def address_verified(name):
	rica = frappe.get_doc('RICA Submission', name)
	if rica.region != None or rica.region!='':
		if rica.city != None or rica.city != '':
			if rica.surburb != None or rica.surburb != '':
				if rica.address1 != None or rica.address != '':
					rica.address_verified = True
					rica.address_verified_on = frappe.utils.now_datetime()
					rica.save()
				else:
					frappe.msgprint('Please enter address data')
			else:
				frappe.msgprint('Please enter surburb data')
		else:
			frappe.msgprint('Please enter city data')
	else:
		frappe.msgprint('Please enter region data')
	rica_sim(name)

#@frappe.whitelist(allow_guest=False)
#def rica_sim(name, inform_referrer = True):
#	# frappe.msgprint('checking for rica: ' + name)
#	rica = frappe.get_doc('RICA Submission',name)
#	result=''
#	if rica.name_verified and rica.identity_number_verified and rica.address_verified:
#		for s in rica.get('sims_to_rica'):
#			if not s.ricaed:
#				# frappe.msgprint("Rica API for " + s.serial_no)
#				result = s.rica_logs
#				data = frappe.get_doc("MTN Services Settings")
#				data.rica_password = frappe.utils.password.get_decrypted_password('MTN Services Settings',
#																				  'MTN Services Settings',
#																				  'rica_password', False)
#				data.sms_password = frappe.utils.password.get_decrypted_password('MTN Services Settings',
#																				  'MTN Services Settings',
#																				  'sms_password', False)
#
#				frappe.msgprint(data.rica_password)
#				driver = webdriver.PhantomJS()
#				driver.set_window_size(1120, 550)
#				driver.get(data.rica_login_url)
#				# frappe.msgprint(driver.current_url)
#				driver.find_element_by_id('txtId').send_keys(data.rica_username)
#				driver.find_element_by_id("txtPassword").send_keys(data.rica_password)
#				driver.find_element_by_id("btnLogin").click()
#
#				# frappe.msgprint(driver.current_url)
#				# frappe.msgprint(data.rica_register_url)
#
#				if driver.current_url == data.rica_menu_url:
#					# frappe.msgprint("Login successful")
#					result = '\n\n| %s | %s |' % (frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),'Login successful')
#					driver.get(data.rica_register_url)
#					if rica.is_consumer == True:
#						driver.find_element_by_id('lstCustType').send_keys("C")
#					else:
#						driver.find_element_by_id('lstCustType').send_keys("J")
#
#					driver.find_element_by_id('txtFName').send_keys(rica.first_names)
#					driver.find_element_by_id('txtSurname').send_keys(rica.last_names)
#					if rica.is_citizen == True:
#						driver.find_element_by_id('optSA').send_keys("I")
#					else:
#						driver.find_element_by_id('optSA').send_keys("P")
#					driver.find_element_by_id('txtID').send_keys(rica.identification_number)
#					driver.find_element_by_id('lstResRegion').send_keys(rica.region)
#					time.sleep(1)
#					driver.find_element_by_id('txtResCityTown').send_keys(rica.city)
#					time.sleep(1)
#					driver.find_element_by_id('txtResSuburb').send_keys(rica.surburb)
#					driver.find_element_by_id('txtResAddr1').send_keys(rica.address1)
#					driver.find_element_by_id('txtResAddr2').send_keys(rica.address2)
#					driver.find_element_by_id('txtResAddr3').send_keys(rica.address3)
#					driver.find_element_by_id('txtResCode').send_keys(rica.code)
#
#					# self.driver.find_element_by_id('txtMSISDN').send_keys("7203245157089")
#					# time.sleep(1)
#
#					driver.find_element_by_id('txtSIM').send_keys(s.serial_no)
#					time.sleep(1)
#					driver.find_element_by_id("btnAddSIM").click()
#
#					# self.driver.find_element_by_id('txtSIMKit').send_keys("")
#					time.sleep(2)
#					driver.find_element_by_id("lnkSubmit").click()
#					time.sleep(3)
#					result += '\n| %s | %s |' % (
#					frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), driver.current_url)
#					index = driver.page_source.find('>alert(')
#					if index != -1:
#						end = driver.page_source.find(');', index + 1)
#						alert_message = driver.page_source[(index + 8):end - 3]
#						result += '\n| %s | %s |' % (
#							frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),
#							alert_message)
#					elif 'successful' in driver.page_source:
#						result += "Successfully RICA'd"
#						s.ricaed = True
#						s.ricaed_on = frappe.utils.now_datetime()
#						customer = frappe.get_doc('Varmani Network', rica.customer)
#						if inform_referrer:
#							referrer = frappe.get_doc('Varmani Network', customer.parent_varmani_network)
#							message = 'Sim: ' + s.serial_no + ' given to ' + customer.name + ' has been RICAed. Please assist now to active the sim'
#							# responseMeg = "<usareq NODE='" + data.sms_node + "' TRANSFORM='SUBMIT_SM' USERNAME='" + data.sms_username + "' PASSWORD='" + data.sms_password + "'><command><submit_sm><a_number>" + data.sms_a_number + "</a_number><b_number>" + referrer.msisdn + "</b_number><service_type></service_type><message>"+ message +"</message><registered_delivery></registered_delivery></submit_sm></command></usareq>"
#							# response = requests.post(data.message_url, data={'command': responseMeg})
#							## response = myMessenger.sendSMS(referrer.msisdn, message)
#							result += '\n| %s | %s |' % (
#							frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),
#							message)  # response.status_code + message)
#						else:
#							message = 'Sim: ' + s.serial_no + ' has been RICAed. You can now active the sim'
#							responseMeg = "<usareq NODE='" + data.sms_node + "' TRANSFORM='SUBMIT_SM' USERNAME='" + data.sms_username + "' PASSWORD='" + data.sms_password + "'><command><submit_sm><a_number>" + data.sms_a_number + "</a_number><b_number>" + customer.msisdn + "</b_number><service_type></service_type><message>" + message + "</message><registered_delivery></registered_delivery></submit_sm></command></usareq>"
#							# response = requests.post(data.message_url, data={'command': responseMeg})
#							## response = myMessenger.sendSMS(referrer.msisdn, message)
#							result += '\n| %s | %s |' % (
#								frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), message)
#						# response.status_code + message)
#					else:
#						result += '\n| %s | %s |' % (frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),'Failed')
#
#					# frappe.msgprint(result)
#					s.rica_logs = result
#					# frappe.msgprint(s)
#					# frappe.msgprint(rica)
#					# s.ricaed = True
#					rica.save()
#					# frappe.db.commit()
#					frappe.msgprint(result)
#					driver.quit()
#				else:
#					frappe.msgprint('Login failed')
#
#			if s.to_be_invoiced:
#				pass
