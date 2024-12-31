# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	mop = frappe.db.sql_list("select name from `tabMode of Payment` order by name asc")
	columns, data = [], []

	columns = get_columns(mop)
	data = get_data(filters, mop)
	
	# if not data:
	# 	frappe.msgprint(_("No records found"))
	# 	return columns,data
	

	return columns, data

def get_columns(mop):
	columns = [
			{
				"fieldname": "sales_partner",
				"label":_("Sales Partner"),
				"fieldtype": "Link",
				"options": "Sales Partner",
				"width":'350'
			},
			{
				"fieldname": "total_sales",
				"label":_("Total Sales"),
				"fieldtype": "Currency",
				"width":'200'
			},
			{
				"fieldname": "total_return",
				"label":_("Total Return"),
				"fieldtype": "Currency",
				"width":'200'
			},
			{
				"fieldname": "net_sales",
				"label":_("Net Sales"),
				"fieldtype": "Currency",
				"width":'200'
			},
			{
				"fieldname": "total_sales_invoice",
				"label":_("Total Sales Invoice"),
				"fieldtype": "Int",
				"width":'200'
			},
			{
				"fieldname": "total_sales_return",
				"label":_("Total Sales Return"),
				"fieldtype": "Int",
				"width":'200'
			},
		]
	
	for col in mop:
		columns.append(
				{
				"fieldname": _(col),
				"label":_(col),
				"fieldtype": "Currency",
				"width":'160'
			})

	# print(columns , '====columns')
	return columns

def get_conditions(filters):
	conditions = {
		"company": filters.company,
	}
	if filters.get("from_date") > filters.get("to_date"):
		frappe.throw(_("From Date Cann't Be Greater Than To Date."))
	else:
		conditions.update({"from_date": filters.get("from_date")})
		conditions.update({"to_date": filters.get("to_date")})
	if filters.get("sales_partner"):
		conditions.update({"sales_partner": filters.get("sales_partner")})

	return conditions

def get_data(filters, mop):
	conditions = get_conditions(filters)
	data = []

	si = frappe.db.sql("""
			SELECT
				IFNULL(si.sales_partner,'') as sales_partner,
				sum(si.grand_total) as total_sales,
				count(si.name) as total_no_of_sales_invoice
			FROM
				`tabSales Invoice` si
			where
				si.is_return = 0
			group by
				si.sales_partner
		""", as_dict=1)
	
	print(si, "=======si")
	
	return_si = frappe.db.sql("""
			SELECT
				IFNULL(si.sales_partner,'') as sales_partner,
				sum(si.grand_total) as total_return,
				count(si.name) as total_no_of_credit_notes
			FROM
				`tabSales Invoice` si
			where
				si.is_return = 1
			group by
				si.sales_partner
		""", as_dict=1)
	
	print(return_si, "===return_si")

	for row in si:
		for credit in return_si:
			if row.sales_partner == credit.sales_partner:
				data.append({
					"sales_partner": row.sales_partner,
					"total_sales": row.total_sales,
					"total_return": credit.total_return,
					"net_sales": row.total_sales + credit.total_return,
					"total_sales_invoice": row.total_no_of_sales_invoice,
					"total_sales_return": credit.total_no_of_credit_notes
				})
				break
	
	mop_data = frappe.db.sql("""SELECT
					IFNULL(si.sales_partner,'') as sales_partner,
					sip.mode_of_payment ,
					sum(sip.amount) as mod_amout
				FROM
					`tabSales Invoice` si
				left outer join `tabSales Invoice Payment` sip on
					si.name = sip.parent
				group by
					si.sales_partner,
					sip.mode_of_payment""", as_dict=1)

	final_data = []
	for main_row in data:
		found=False
		for mop_row in mop_data:
			print("===========")
			if main_row.get('sales_partner') == mop_row.get('sales_partner'):
				for mop_type in mop:
					if mop_row.get('mode_of_payment') == mop_type:
						print(main_row,'mainrow')
						main_row.update({_(mop_type): mop_row['mod_amout']})
						final_data.append(main_row)
						found=True
						print(final_data,'-----aftermainrow')
		
		if found==False:
			final_data.append(main_row)
	return final_data

