from __future__ import unicode_literals
import pdb
import frappe, json
from frappe import _, msgprint, throw

@frappe.whitelist(allow_guest=False)
def get_glocell_invoices():
    supplier_invoices = frappe.db.sql("""SELECT name, bill_no, bill_date
                                      FROM `tabPurchase Invoice`
                                      where supplier_name = 'Glocell (Pty) Ltd'
                                      order by bill_date desc""",as_dict=False)
    return supplier_invoices

@frappe.whitelist(allow_guest=False)
def get_customer_invoice(supplier_invoice_no):
    sales_invoice = {}
    try:
        name = frappe.db.exists('Sales Invoice', {'remarks': supplier_invoice_no})
        if name:
            sales_invoice = frappe.get_doc('Sales Invoice', name)
    except:
        sales_invoice = supplier_invoice_no


    return sales_invoice


@frappe.whitelist(allow_guest=False)
def get_payment_entry(supplier):
    entries = frappe.get_all('Payment Entry', filters={'party_name': supplier}, fields=['name'])
    return entries
    list = {}
    for e in entries:
        list.append(e.name)
    return list


@frappe.whitelist(allow_guest=False)
def cancel_payment_entry(name):
    e = frappe.get_doc('Payment Entry', name)
    e.cancel()
    deleted = frappe.delete_doc('Payment Entry', name)
    frappe.db.commit()

    return 'Done'


@frappe.whitelist(allow_guest=False)
def cancel_customer_invoice(name):
    e = frappe.get_doc('Sales Invoice', name)
    e.cancel()
    deleted = frappe.delete_doc('Sales Invoice', name)
    frappe.db.commit()

    return 'Done'


@frappe.whitelist(allow_guest=False)
def cancel_supplier_invoice(name):
    e = frappe.get_doc('Purchase Invoice', name)
    e.cancel()
    deleted = frappe.delete_doc('Purchase Invoice', name)
    frappe.db.commit()

    return 'Done'
