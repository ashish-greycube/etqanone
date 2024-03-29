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
	data =execute(filters)
	for res in data:
		for row in res:
			print('row',row)
			if row.get('gl_entry'):
				if row.get('voucher_type')=='Sales Invoice':
					row['remarks']=row.get('voucher_no')
					is_return=frappe.db.get_value(row.get('voucher_type'), row.get('voucher_no'), 'is_return')
					if is_return==1:
						row['voucher_type']='Sales Return'
				elif row.get('voucher_type')=='Payment Entry':
					remark=frappe.db.get_value(row.get('voucher_type'), row.get('voucher_no'), 'remark')
					if remark:
						row['remarks']=remark
				elif row.get('voucher_type')=='Journal Entry':
					remark=frappe.db.get_value(row.get('voucher_type'), row.get('voucher_no'), 'jv_remark')
					if remark:
						row['remarks']=remark						
	return data