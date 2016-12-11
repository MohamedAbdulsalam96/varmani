from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "MSISDN Communications",
					"description": _("MTN USSD Messages")
				},
				{
					"type": "doctype",
					"name": "Varmani Network",
					"description": _("Customers in the network.")
				},
				{
					"type": "page",
					"name": "network-browser",
					"icon": "icon-sitemap",
					"label": _("Network of Customers"),
					"route": "network-browser",
					"description": _("Tree of varmani customers."),
					"doctype": "Network Customer",
				},
				{
					"type": "doctype",
					"name": "Banned MSISDN",
					"description": _("Banned MSISDN List.")
				},
				{
					"type": "doctype",
					"name": "SMS Customer",
					"description": _("Customers using SMS as a service.")
				},
				{
					"type": "doctype",
					"name": "RICA Submission",
					"description": _("Customers RICA details.")
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "MTN Services Settings",
                    "description": _("MTN Service settings.")
				},
				{
					"type": "doctype",
					"name": "USSD Menu",
					"description": _("USSD Menus.")
				},
				{
					"type": "page",
					"name": "ussd-menu",
					"icon": "icon-sitemap",
					"label": _("Ussd Menu Configuration"),
					"route": "ussd-menu",
					"description": _("Tree of menu options for ussd customers."),
					"doctype": "USSD Menu",
				},
				{
					"type": "doctype",
					"name": "Commission Structure",
					"description": _("Commission Structure for products sold on the Varmani Network")
				},
				{
					"type": "doctype",
					"name": "Network Account Settings",
					"description": _("Network Account Settings.")
				}
			]
		}
	]
