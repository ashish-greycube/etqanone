# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict

def execute(filters=None):
	from erpnext.accounts.report.general_ledger.general_ledger import execute
	
	if not filters:
		return [], []
	if filters.get("party"):
		filters.party = frappe.parse_json(filters.get("party"))
	else:
		frappe.throw(_("Select a customer in party field"))

	return execute(filters)