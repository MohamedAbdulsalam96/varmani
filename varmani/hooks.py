# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "varmani"
app_title = "Varmani"
app_publisher = "Hemant Pema"
app_description = "Varmani Network Management Application"
app_icon = "octicon octicon-file-directory"
app_color = "red"
app_email = "hem@varmani.co.za"
app_version = "1.0.0"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/varmani/css/varmani.css"
# app_include_js = "/assets/varmani/js/varmani.js"

# include js, css files in header of web template
# web_include_css = "/assets/varmani/css/varmani.css"
# web_include_js = "/assets/varmani/js/varmani.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
#home_page = "index"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "varmani.install.before_install"
# after_install = "varmani.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "varmani.varmani.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }
has_website_permission = {
	"Customer": "varmani.varmani.doctype.varmani_network.varmani_network.referral",
	"Varmani Network": "varmani.varmani.doctype.varmani_network.varmani_network.referral",
	"User":""
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Payment Entry": {
		#"on_submit": "varmani.varmani.doctype.varmani_network.varmani_network.is_commission_due"
		"on_cancel": "varmani.varmani.doctype.varmani_network.varmani_network.is_payment_deleted"
   },
	"GL Entry": {
		"before_save": "varmani.varmani.doctype.varmani_network.varmani_network.update_party",
		"on_submit": "varmani.varmani.doctype.varmani_network.varmani_network.is_commission_due"
	}
	#"Journal Entry Account":{

#   },
#	"Contact": {
#		"validate": "varmani.varmani.custom.get_custom_series"
#    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"varmani.tasks.all"
# 	],
# 	"daily": [
# 		"varmani.tasks.daily"
# 	],
# 	"hourly": [
# 		"varmani.tasks.hourly"
# 	],
# 	"weekly": [
# 		"varmani.tasks.weekly"
# 	]
# 	"monthly": [
# 		"varmani.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "varmani.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "varmani.event.get_events"
# }

fixtures = ["Custom Field"]