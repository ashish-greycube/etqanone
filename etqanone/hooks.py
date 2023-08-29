# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "etqanone"
app_title = "Etqanone"
app_publisher = "GreyCube Technologies"
app_description = "Etqanone for v13"
app_icon = "fa fa-paint-brush"
app_color = "gold"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/etqanone/css/etqanone.css"
# app_include_js = "/assets/etqanone/js/etqanone.js"

# include js, css files in header of web template
# web_include_css = "/assets/etqanone/css/etqanone.css"
# web_include_js = "/assets/etqanone/js/etqanone.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
website_context = {
    "favicon": "/assets/etqanone/images/icon.png",
    "splash_image": "/assets/etqanone/images/splash.png",
}

# application home page (will override Website Settings)
# home_page = "login"
# after_install = "etqanone.api.import_arabic_translation"
# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "etqanone.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "etqanone.install.before_install"
# after_install = "etqanone.install.after_install"
after_migrate = "etqanone.migrations.after_migrations"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "etqanone.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {"on_submit": "etqanone.api.on_submit_sales_invoice"}
    # 	"*": {
    # 		"on_update": "method",
    # 		"on_cancel": "method",
    # 		"on_trash": "method"
    # 	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"etqanone.tasks.all"
# 	],
# 	"daily": [
# 		"etqanone.tasks.daily"
# 	],
# 	"hourly": [
# 		"etqanone.tasks.hourly"
# 	],
# 	"weekly": [
# 		"etqanone.tasks.weekly"
# 	]
# 	"monthly": [
# 		"etqanone.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "etqanone.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "etqanone.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "etqanone.task.get_dashboard_data"
# }
