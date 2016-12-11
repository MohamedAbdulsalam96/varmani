# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import flt
from erpnext.accounts.utils import get_balance_on
from erpnext.accounts.report.financial_statements import sort_root_accounts

@frappe.whitelist()
def get_companies():
	"""get a list of companies based on permission"""
	return [d.name for d in frappe.get_list("Company", fields=["name"],
		order_by="name")]

@frappe.whitelist()
def get_children():
	args = frappe.local.form_dict
	ctype, company = args['ctype'], args['comp']
	fieldname = frappe.db.escape(ctype.lower().replace(' ','_'))
	#frappe.msgprint(fieldname)
	doctype = frappe.db.escape(ctype)

	#frappe.msgprint("This is args",0)
	#frappe.msgprint(args,0)
	#frappe.msgprint(args['parent'])

	# root
	if args['parent'] == 'Varmani Network': # "Cost Centers"):
		fields = ', full_name'
		acc = frappe.db.sql(""" select name as value, 1 as expandable, full_name
			from `tab{doctype}`
			where ifnull(`parent_{fieldname}`,'') = ''
			and docstatus<2
			order by name""".format(fields=fields, fieldname = fieldname, doctype=doctype), as_dict=1)

		#frappe.msgprint("Did acc query run",0)
		#frappe.msgprint(acc,0)

		#if args["parent"]=="Varmani Network":
		#	frappe.msgprint("sorting needed",0)
			#sort_root_accounts(acc)
	else:
		# other
		parentName = args['parent']
		#frappe.msgprint("Not ROOT ")# + fullname)
		fields = ", full_name" #if ctype=="Account" else ""
		#parentName = frappe.db.get_value(doctype,{'full_name':fullname})
		#frappe.msgprint(parentName,0)
		#parent = acc[0]
		#frappe.msgprint(acc,0)
		acc = frappe.db.sql("""select name as value, 1 as expandable, parent_{fieldname} as parent, full_name from `tab{doctype}` where ifnull(`parent_{fieldname}`,'') = %s and docstatus<2 order by name""".format(fieldname=fieldname, doctype=doctype), parentName, as_dict=1)


	#frappe.msgprint("This is query result",0)
	#frappe.msgprint(acc,0)
	return acc
