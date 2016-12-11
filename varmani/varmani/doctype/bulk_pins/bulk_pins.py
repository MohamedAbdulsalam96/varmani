# -*- coding: utf-8 -*-
# Copyright (c) 2015, Hemant Pema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BulkPins(Document):
	pass

@frappe.whitelist(allow_guest=False)
def get_items():
	items = frappe.get_all('Item')
	return items

@frappe.whitelist(allow_guest=False)
def load_pin(serial,item):

	# counter =0
	# for i in items:
	# 	for x in range(1,3000):
	# 		if (counter%1000)==0:
	# 			frappe.db.commit()

	bulkpin = frappe.new_doc('Bulk Pins')
	bulkpin.pin = "1234"
	bulkpin.serial_number = serial#item + ' - ' + str(frappe.utils.now_datetime())
	bulkpin.item_code = item
	bulkpin.insert()
	frappe.db.commit()
    #
	# return True