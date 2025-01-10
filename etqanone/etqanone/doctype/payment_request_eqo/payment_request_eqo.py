# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from erpnext import get_default_currency
from frappe.model.document import Document
from frappe.utils import today
from erpnext.accounts.doctype.payment_entry.payment_entry import (get_bank_cash_account, get_party_details)
from frappe.model.mapper import get_mapped_doc
# from erpnext.accounts.doctype.bank_account.bank_account import (get_party_bank_account)

class PaymentRequestEqo(Document):
	def validate(self):
		self.set_details_for_expense_payment()
		self.calculate_supplier_payment_total()
		self.calculate_customer_payment_total()
		self.set_details_for_employee_payment()

	def on_submit(self):
		self.check_sanctioned_amount()
		# self.create_jv_for_expense_payment()
		# self.create_payment_entry_for_party()

	def set_details_for_expense_payment(self):
		if self.pay_to == "Expense":
			company = erpnext.get_default_company()
			purchase_tax_chanrges_list = frappe.db.get_all("Purchase Taxes and Charges Template", filters={"is_default":1, "company":company},
													fields=["name"], limit=1)
			
			tax_amount = 0
			total_expense_amount = 0
			if len(purchase_tax_chanrges_list) > 0:
				for tax in purchase_tax_chanrges_list:
					print(tax.name, "========tax.name")
					doc = frappe.get_doc("Purchase Taxes and Charges Template", tax.name)
					if len(doc.taxes) > 0:
						tax_amount = doc.taxes[0].rate
			else:
				frappe.msgprint(_("No Default Purchase Tax Amount Found."), alert=1)
			
			if len(self.expense_payment_request_details) > 0:
				for expense in self.expense_payment_request_details:
					if not expense.cost_center:
						expense.cost_center = self.cost_center
					if not expense.project:
						expense.project = self.project
					if expense.tax_applicable == "Yes":
						expense.tax_amount = (expense.sanctioned_amount or 0) * (tax_amount / 100)

					expense.total_amount = (expense.sanctioned_amount or 0) + (expense.tax_amount or 0)
			
					if expense.action == "Approve":
						total_expense_amount = total_expense_amount + expense.total_amount

			self.total_expense_amount = total_expense_amount

	def calculate_supplier_payment_total(self):
		if self.pay_to == "Supplier":
			if len(self.supplier_payment_request_details) > 0:
				total_payment_amount = 0
				for sup in self.supplier_payment_request_details:
					total_payment_amount = total_payment_amount + sup.payment_amount

				self.total_payment_request_amount = total_payment_amount

	def calculate_customer_payment_total(self):
		if self.pay_to == "Customer":
			if len(self.customer_payment_request_details) > 0:
				total_payment_amount = 0
				for cus in self.customer_payment_request_details:
					total_payment_amount = total_payment_amount + cus.payment_amount

				self.total_payment_request_amount = total_payment_amount

	def set_details_for_employee_payment(self):
		if self.pay_to == "Employee":
			company = erpnext.get_default_company()
			purchase_tax_chanrges_list = frappe.db.get_all("Purchase Taxes and Charges Template", filters={"is_default":1, "company":company},
													fields=["name"], limit=1)
			
			tax_amount = 0
			total_payment_amount = 0
			if len(purchase_tax_chanrges_list) > 0:
				for tax in purchase_tax_chanrges_list:
					print(tax.name, "========tax.name")
					doc = frappe.get_doc("Purchase Taxes and Charges Template", tax.name)
					if len(doc.taxes) > 0:
						tax_amount = doc.taxes[0].rate

			if len(self.employee_payment_request_details) > 0:	
				for emp in self.employee_payment_request_details:
					if emp.tax_applicable == "Yes":
						emp.tax_amount = emp.amount * (tax_amount / 100)
					emp.total_amount = emp.amount + emp.tax_amount
					total_payment_amount = total_payment_amount + emp.total_amount

				self.total_payment_request_amount = total_payment_amount

	def check_sanctioned_amount(self):
		if self.pay_to == "Expense" and len(self.expense_payment_request_details) > 0:
			for exp in self.expense_payment_request_details:
				if exp.sanctioned_amount == None or exp.sanctioned_amount == 0:
					frappe.throw(_("In Row {0}: Please Set Sanctioned Amount.").format(exp.idx))
				else:
					continue

	def create_jv_for_expense_payment(self):
		if self.pay_to == "Expense":
			jv = frappe.new_doc("Journal Entry")
			jv.voucher_type = "Journal Entry"
			jv.posting_date = self.request_date

			accounts = []
			if len(self.expense_payment_request_details) > 0:
				total_tax_amount = 0
				
				## debit expense accounts
				for expense in self.expense_payment_request_details:
					if expense.action == "Approve":
						accounts_row = {
							"account":expense.expense_account,
							"cost_center":expense.cost_center,
							"project":expense.project,
							"debit_in_account_currency":expense.sanctioned_amount,
						}

						accounts.append(accounts_row)
						if expense.tax_applicable == "Yes":
							total_tax_amount = total_tax_amount + expense.tax_amount

				## debit tax expense account
				company = erpnext.get_default_company()
				if total_tax_amount > 0:
					purchase_tax_chanrges_list = frappe.db.get_all("Purchase Taxes and Charges Template", filters={"is_default":1, "company":company},
													fields=["name"], limit=1)
					
					if len(purchase_tax_chanrges_list) > 0:
						for tax in purchase_tax_chanrges_list:
							doc = frappe.get_doc("Purchase Taxes and Charges Template", tax.name)
							if len(doc.taxes) > 0:
								tax_account = doc.taxes[0].account_head

								tax_account_row = {
										"account":tax_account,
										"cost_center":self.cost_center,
										"project":self.project,
										"debit_in_account_currency":total_tax_amount,
									}
								
								accounts.append(tax_account_row)

				## total credit expense account
				mop = frappe.get_doc("Mode of Payment", self.mode_of_payment)
				credit_acc = ""
				if len(mop.accounts) > 0:
					credit_acc = mop.accounts[0].default_account

				if credit_acc == "":
					frappe.throw(_("Please set default account in Mode Of Payment."))
				else:
					credit_account_row = {
									"account":credit_acc,
									"cost_center":self.cost_center,
									"project":self.project,
									"credit_in_account_currency":self.total_expense_amount,
								}
					
					accounts.append(credit_account_row)

			jv.set("accounts",accounts)
			jv.run_method('set_missing_values')
			jv.save(ignore_permissions=True)
			frappe.msgprint(_("Journal Entry {0} Created For Expense Payment.").format(jv.name), alert=1)
			self.journal_entry = jv.name
			jv.submit()

	def create_payment_entry_for_party(self):
		if self.pay_to == "Supplier": 
			self.create_payment_entry("Pay")
		elif self.pay_to == "Customer":
			self.create_payment_entry("Receive")
		elif self.pay_to == "Employee":
			self.create_payment_entry("Pay")

	def create_payment_entry(self, payment_type):
	 
		bank_account = None

		#### get party account details ###
		party_details = get_party_details(self.company, self.party_type, self.party_no, today(), cost_center=None)	

		#### get mode of payment account ####
		bank = get_bank_cash_account(self, bank_account)
		
		# if self.party_type in ["Customer", "Supplier"] and not bank:
		# 	party_bank_account = get_party_bank_account(self.party_type, self.party_no)
		# 	if party_bank_account:
		# 		account = frappe.db.get_value("Bank Account", party_bank_account, "account")
		# 		bank = get_bank_cash_account(self, account)


		pe = frappe.new_doc("Payment Entry")
		pe.naming_series = "ACC-PAY-.YYYY.-"
		pe.posting_date = self.request_date
		pe.payment_type = payment_type
		pe.mode_of_payment = self.mode_of_payment
		pe.party_type = self.party_type
		pe.party = self.party_no
		pe.party_name = self.party_name
		pe.company = self.company
		pe.reference_no = self.name
		pe.reference_date = today()
		pe.paid_amount = self.total_payment_request_amount
		pe.received_amount = self.total_payment_request_amount
		# pe.target_exchange_rate = 1
		# pe.source_exchange_rate = 1
		# pe.paid_from_account_currency = get_default_currency()
		# pe.paid_to_account_currency = get_default_currency()

		print(party_details, "======party_account")
		print(bank, "===========bank")
		pe.paid_from = party_details.get("party_account") if payment_type == "Receive" else bank.account
		pe.paid_to = party_details.get("party_account") if payment_type == "Pay" else bank.account

		paid_to_acc = ""
		if payment_type == "Pay":
			if self.party_type == "Employee":
				paid_to_acc = self.employee_paid_to_account
			else:
				paid_to_acc = party_details.get("party_account")
		else:
			paid_to_acc = bank.account

		pe.paid_to = paid_to_acc

		pe.paid_from_account_currency = party_details.get("party_account_currency") if payment_type == "Receive" else bank.account_currency
		pe.paid_to_account_currency = party_details.get("party_account_currency") if payment_type == "Pay" else bank.account_currency

		pe.ensure_supplier_is_not_blocked()
		pe.validate()
		# pe.set_received_amount()
		# pe.setup_party_account_field()
		pe.set_missing_values()
		# pe.set_missing_ref_details()
		pe.set_exchange_rate()

		# pe.run_method("onload")
		# pe.run_method("set_missing_values")
		pe.save(ignore_permissions=True)
		self.payment_entry = pe.name
		pe.submit()
		frappe.msgprint(_("Payment Entry {0} Created.").format(pe.name), alert=1)

@frappe.whitelist()
def get_payment_entry(docname):
	payment_entry_found = False

	pe_list = frappe.db.get_all('Payment Entry', filters={'custom_payment_request_reference':docname}, fields=['name'])

	# print(pe_list, "------pe_list")
	if len(pe_list) > 0:
		payment_entry_found = True
	
	return payment_entry_found

@frappe.whitelist()
def get_journal_entry(docname):
	journal_entry_found = False

	jv_list = frappe.db.get_all('Journal Entry', filters={'custom_payment_request_reference':docname}, fields=['name'])

	# print(jv_list, "------jv_list")
	if len(jv_list) > 0:
		journal_entry_found = True
	
	return journal_entry_found



@frappe.whitelist()
def get_expense_account(expense_type):

	expense_type_doc = frappe.get_doc("Expense Claim Type", expense_type)
	if len(expense_type_doc.accounts) > 0:
		expense_acc = expense_type_doc.accounts[0].default_account
		return expense_acc
	else:
		frappe.throw(_("Please Set Defaul Expense Acoount in Expense Claim Type."))


@frappe.whitelist()
def create_jv_for_expense_payment(source_name, target_doc=None):
	print("Inside fucntion!!!")
	def postprocess(source, target):
		doc = frappe.get_doc("Payment Request Eqo", source_name)
		target.voucher_type = "Journal Entry"
		target.posting_date = doc.request_date

		accounts = []
		total_tax_amount = 0
		for exp in doc.expense_payment_request_details:
			if exp.action == "Approve":
				accounts_row = {
					"account":exp.expense_account,
					"cost_center":exp.cost_center,
					"project":exp.project,
					"debit_in_account_currency":exp.sanctioned_amount,
					}

				accounts.append(accounts_row)

				if exp.tax_applicable == "Yes":
					total_tax_amount = total_tax_amount + exp.tax_amount
		
		if total_tax_amount > 0:
			purchase_tax_chanrges_list = frappe.db.get_all("Purchase Taxes and Charges Template", filters={"is_default":1, "company":doc.company},
											fields=["name"], limit=1)
			
			if len(purchase_tax_chanrges_list) > 0:
				for tax in purchase_tax_chanrges_list:
					tax_doc = frappe.get_doc("Purchase Taxes and Charges Template", tax.name)
					if len(tax_doc.taxes) > 0:
						tax_account = tax_doc.taxes[0].account_head
						tax_account_row = {
							"account":tax_account,
							"cost_center":doc.cost_center,
							"project":doc.project,
							"debit_in_account_currency":total_tax_amount,
							}
						accounts.append(tax_account_row)

		target.set("accounts",accounts)
		target.run_method("set_missing_values")

	doc = get_mapped_doc(
		"Payment Request Eqo",
		source_name,
		{
			"Payment Request Eqo": {
				"doctype": "Journal Entry",
				"field_map": {
					"custom_payment_request_reference": "name",
				}
			},
			# "Expense Payment Request Details Eqo": {
			# 	"doctype": "Journal Entry Account",
			# 	"field_map": {
			# 		"custom_sample_request_reference": "name",
			# 	}
			# }
		},
		target_doc,
		postprocess,
	)
	print(doc.name, "===docname")
	return doc

@frappe.whitelist()
def create_payment_entry(source_name, target_doc=None):
	print("Inside fucntion!!!")
	def postprocess(source, target):
		doc = frappe.get_doc("Payment Request Eqo", source_name)
		target.naming_series = "ACC-PAY-.YYYY.-"
		target.posting_date = doc.request_date

		# target.payment_type = doc.payment_type
		if doc.pay_to == "Supplier":
			target.payment_type = "Pay"
		elif doc.pay_to == "Customer":
			target.payment_type = "Receive"
		elif doc.pay_to == "Employee":
			target.payment_type = "Pay"

		target.party = doc.party_no
		target.party_type = doc.party_type
		target.party_name = doc.party_name
		target.company = doc.company
		# target.reference_no = doc.name
		# target.reference_date = today()
		target.paid_amount = doc.total_payment_request_amount
		target.received_amount = doc.total_payment_request_amount

		#### get party account details ###
		party_details = get_party_details(doc.company, doc.party_type, doc.party_no, today(), cost_center=None)

		target.paid_from = party_details.get("party_account") if target.payment_type == "Receive" else ''
		target.paid_to = party_details.get("party_account") if target.payment_type == "Pay" else ''

		target.paid_from_account_currency = party_details.get("party_account_currency") if target.payment_type == "Receive" else get_default_currency()
		target.paid_to_account_currency = party_details.get("party_account_currency") if target.payment_type == "Pay" else get_default_currency()

		# target.run_method("set_missing_values")

	doc = get_mapped_doc(
		"Payment Request Eqo",
		source_name,
		{
			"Payment Request Eqo": {
				"doctype": "Payment Entry",
				"field_map": {
					"custom_payment_request_reference": "name",
				}
			},
		},
		target_doc,
		postprocess,
	)
	print(doc.name, "===docname")
	return doc