from __future__ import unicode_literals
import pdb
import frappe, json
from frappe import _, msgprint, throw


def get_custom_series(doc, method=None):
	if doc.doctype == 'Customer':
		surfix = "C"
		prefix = doc.customer_name[:3]
	elif doc.doctype == 'Supplier':
		surfix = "S"
		prefix = doc.supplier_name[:3]
	elif doc.doctype == 'Contact':
		surfix = "P"
		prefix = doc.first_name[:3]
	try:
		name = frappe.get_value(doc.doctype, doc.name, 'name')
		if name == None:
			doc.name = get_series(doc, prefix, surfix)
			return doc
		else:
			pass
	except:
		# frappe.msgprint(_("Something broke"))
		doc.name = get_series(doc, prefix, surfix)
		return doc


def get_series(doc, prefix, surfix):
	if doc.doctype == 'Customer':
		name = frappe.get_value('Customer', {'customer_name': doc.customer_name}, 'name')
		if name:
			customer = frappe.get_doc('Customer', name)
		else:
			return check_series(doc, prefix, surfix)

		if doc.tax_id == None or doc.tax_id == '':
			doctax_id = 'Unknown'
		else:
			doctax_id = doc.tax_id

		if customer.tax_id == None or customer.tax_id == '':
			customertax_id = 'Unknown'
		else:
			customertax_id = customer.tax_id

		# frappe.msgprint(_(doctax_id))
		# frappe.msgprint(_(customertax_id))

		if customertax_id != 'Unknown':
			if doctax_id != 'Unknown':
				if customertax_id == doctax_id:
					return customer.name
				else:
					return check_series(doc, prefix, surfix)
			else:
				return customer.name
		else:
			return customer.name

	elif doc.doctype == 'Supplier':
		name = frappe.get_value('Supplier', {'supplier_name': doc.supplier_name}, 'name')

		if name:
			supplier = frappe.get_doc("Supplier", name)
			return supplier.name
		else:
			return check_series(doc, prefix, surfix)

	elif doc.doctype == 'Contact':
		name = frappe.get_value("Contact", {'first_name': doc.first_name, 'last_name': doc.last_name}, 'name')
		if name:
			contact = frappe.get_doc("Contact", name)
		else:
			return check_series(doc, prefix, surfix)

		if doc.email_id == None or doc.email_id == '':
			docemail_id = 'Unknown'
		else:
			docemail_id = doc.email_id

		if contact.email_id == None or contact.email_id == '':
			contactemail_id = 'Unknown'
		else:
			contactemail_id = contact.email_id

		# frappe.msgprint(_(doctax_id))
		# frappe.msgprint(_(customertax_id))

		if contactemail_id != 'Unknown':
			if docemail_id != 'Unknown':
				if contactemail_id == docemail_id:
					return contact.name
				else:
					return check_series(doc, prefix, surfix)
			else:
				return contact.name
		else:
			return contact.name


def check_series(doc, prefix, surfix):
	# frappe.msgprint(prefix, surfix)
	countCustomer = \
	frappe.db.sql("select count(`name`) as n from `tabCustomer` where customer_name like '" + prefix.upper() + "%'")[0][
		0]
	countSupplier = \
	frappe.db.sql("select count(`name`) as n from `tabSupplier` where supplier_name like '" + prefix.upper() + "%'")[0][
		0]
	countContact = \
	frappe.db.sql("select count(`name`) as n from `tabContact` where first_name like '" + prefix.upper() + "%'")[0][0]

	if doc.doctype == 'Customer':
		count = countCustomer + 1
	elif doc.doctype == 'Supplier':
		count = countSupplier + 1
	elif doc.doctype == 'Contact':
		count = countContact + 1

	# frappe.msgprint(count)
	series = prefix.upper() + '{:03d}'.format(count) + surfix

	if doc.doctype == 'Customer':
		while 1:
			countCustomer = \
			frappe.db.sql("select count(`name`) as n from `tabCustomer` where name = '" + series + "'")[0][0]
			if (countCustomer) != 0:
				count = count + 1
				# frappe.msgprint(count)
				series = prefix.upper() + '{:03d}'.format(count) + surfix
			else:
				break
	elif doc.doctype == 'Supplier':
		while 1:
			countSupplier = \
			frappe.db.sql("select count(`name`) as n from `tabSupplier` where name = '" + series + "'")[0][0]
			if (countSupplier) != 0:
				count = count + 1
				# frappe.msgprint(count)
				series = prefix.upper() + '{:03d}'.format(count) + surfix
			else:
				break
	elif doc.doctype == 'Contact':
		while 1:
			countContact = \
			frappe.db.sql("select count(`name`) as n from `tabContact` where name = '" + series + "'")[0][0]
			if (countContact) != 0:
				count = count + 1
				# frappe.msgprint(count)
				series = prefix.upper() + '{:03d}'.format(count) + surfix
			else:
				break
	return series