# Copyright (c) 2024, Greycube and contributors
# For license information, please see license.txt

from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import cstr, getdate
from six import iteritems

from erpnext import get_company_currency, get_default_company
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.utils import get_account_currency
import pandas as pd
# to cache translations
TRANSLATIONS = frappe._dict()
from erpnext.accounts.report.general_ledger import general_ledger


def execute(filters=None):
	print(filters.get('party'))
	if not filters.get('party'):
		return
	
	if filters.get('party'):
		customer=filters.get('party')
		linked_supplier=frappe.db.get_value('Customer', customer, 'linked_customer_supplier_cf')
		if not linked_supplier:
			frappe.throw(_("There is no supplier linked with selected customer"))
		filters['party']=[customer]
	customer_columns, customer_res = general_ledger.execute(filters)

	if linked_supplier:
		filters['party_type']='Supplier'
		filters['party']=[linked_supplier]
		supplier_columns, supplier_res = general_ledger.execute(filters)
		res = customer_res + supplier_res

	account_fields=['debit','credit','debit_in_account_currency','credit_in_account_currency','balance']
	account_opening_dict=frappe._dict({'account': "'Opening'", 'debit': 0.0, 'credit': 0.0, 'debit_in_account_currency': 0.0, 'credit_in_account_currency': 0.0, 'balance': 0.0, 'account_currency': 'SAR', 'bill_no': ''})
	account_total_dict=frappe._dict({'account': "'Total'", 'debit': 0.0, 'credit': 0.0, 'debit_in_account_currency': 0.0, 'credit_in_account_currency': 0.0, 'balance': 0.0, 'account_currency': 'SAR', 'bill_no': ''})
	account_closing_dict=frappe._dict({'account': "'Closing (Opening + Total)'", 'debit': 0.0, 'credit': 0.0, 'debit_in_account_currency': 0.0, 'credit_in_account_currency': 0.0, 'balance': 0.0, 'account_currency': 'SAR', 'bill_no': ''})
	gl_list=[]
	for row in res:
		if row['account']==_("'Opening'"):
			for account_field in account_fields:
				account_opening_dict[account_field]=account_opening_dict[account_field]+row[account_field]
		if row['account']==_("'Total'"):
			for account_field in account_fields:
				account_total_dict[account_field]=account_total_dict[account_field]+row[account_field]
		if row['account']==_("'Closing (Opening + Total)'"):
			for account_field in account_fields:
				account_closing_dict[account_field]=account_closing_dict[account_field]+row[account_field]
		if row.get('gl_entry'):
			gl_list.append(row)

	gl_list.sort(key=lambda x: x['posting_date'], reverse=False)
	current_balance=account_opening_dict.get('balance')
	for gl in gl_list:
		gl['balance']=current_balance+gl['debit']-gl['credit']
		current_balance=gl['balance']
	print(customer_columns,'----',supplier_columns)
	return customer_columns, [account_opening_dict]+gl_list+[account_total_dict]+[account_closing_dict]
