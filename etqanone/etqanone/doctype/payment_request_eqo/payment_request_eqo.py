# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from erpnext import get_default_currency
from frappe.model.document import Document
from frappe.utils import today
from erpnext.accounts.doctype.payment_entry.payment_entry import (get_bank_cash_account, get_party_details)
# from erpnext.accounts.doctype.bank_account.bank_account import (get_party_bank_account)

class PaymentRequestEqo(Document):
	def validate(self):
		self.set_details_for_expense_payment()
		self.calculate_supplier_payment_total()
		self.calculate_customer_payment_total()
		self.set_details_for_employee_payment()
		# self.create_payment_entry_for_party()

	def on_submit(self):
		self.create_jv_for_expense_payment()
		self.create_payment_entry_for_party()

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
			
			if len(self.expense_payment_request_details) > 0:
				for expense in self.expense_payment_request_details:
					if not expense.cost_center:
						expense.cost_center = self.cost_center
					if not expense.project:
						expense.project = self.project
					if expense.tax_applicable == "Yes":
						expense.tax_amount = tax_amount

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
						emp.tax_amount = tax_amount
					emp.total_amount = emp.amount + emp.tax_amount
					total_payment_amount = total_payment_amount + emp.total_amount

				self.total_payment_request_amount = total_payment_amount

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
