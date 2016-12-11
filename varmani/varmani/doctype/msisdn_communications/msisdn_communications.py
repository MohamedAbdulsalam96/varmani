# -*- coding: utf-8 -*-
# Copyright (c) 2015, Hemant Pema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.model.document import Document
import datetime

class MSISDNCommunications(Document):
	pass


@frappe.whitelist()
def banMSISDN(name, msisdn):
	if not frappe.has_permission("MSISDN Communications"):
		frappe.msgprint(_("No Permission"), raise_exception=1)

#try:	#frappe.set_value('USSD Session', sessionId, "banned", True)
	uname = frappe.db.get_value('Banned MSISDN', {'msisdn':msisdn}, 'name')
	#frappe.msgprint(_(uname))
	if not uname:
		#banned = frappe.get_doc("Banned MSISDN", {'msisdn': msisdn})
		newBanned = frappe.new_doc('Banned MSISDN')
		newBanned.msisdn = msisdn
		newBanned.banned_on = datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
		newBanned.insert()

	ussdsession = frappe.get_doc('USSD Session',name)
	ussdsession.db_set('banned',True,update_modified=False)
	frappe.local.flags.commit = True
	return name
