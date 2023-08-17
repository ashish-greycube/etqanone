// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Expense Entry', {
	setup: function (frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value("company", default_company);

		frm.set_query("expense_account", "expenses_entry_detail", function () {
			return {
				filters: {
					'account_type': ["in", ['Expense Account', 'Cost of Goods Sold', 'Expenses Included in Valuation', 'Tax']],
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});	

		frm.set_query("paid_from_account", function () {
			return {
				"filters": {
					"account_type": ["in", ['Bank,Cash']],
					'company': frm.doc.company,
					"is_group": 0
				}
			};
		});
		if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}
		if (frm.doc.expense_type == 'Employee Petty Cash') {
			frm.set_value('party_type', 'Employee');
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);			
		}			
	},
	onload_post_render:async function (frm) {

		if (frm.doc.expense_type == 'Credit') {
			
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);

			frm.set_value('party_type', 'Supplier');
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_payable_account")).message.default_payable_account;
			frm.set_value('payable_account', default_payable_account)

		}
		else if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}	
		else if (frm.doc.expense_type == 'Employee Petty Cash') {
			frm.set_value('party_type', 'Employee');
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);			
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_employee_petty_cash_payable_account_cf")).message.default_employee_petty_cash_payable_account_cf;
			frm.set_value('payable_account', default_payable_account)			
		}				

	},
	expense_type: async function (frm) {
		if (frm.doc.expense_type == 'Credit') {
			
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);

			frm.set_value('party_type', 'Supplier');
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_payable_account")).message.default_payable_account;
			frm.set_value('payable_account', default_payable_account)

		}
		else if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}
		else if (frm.doc.expense_type == 'Employee Petty Cash') {
			frm.set_value('party_type', 'Employee');
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);			
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_employee_petty_cash_payable_account_cf")).message.default_employee_petty_cash_payable_account_cf;
			frm.set_value('payable_account', default_payable_account)			
		}		
	},
	validate: function (frm) {
	if (frm.doc.party_type=='Supplier') {
		for(var i=0;i<=frm.doc.expenses_entry_detail.length-1;i++){
			if (frm.doc.expenses_entry_detail[i].account_type=='Tax'){
	
				if (!frm.doc.expenses_entry_detail[i].supplier && !frm.doc.expenses_entry_detail[i].supplier_name && !frm.doc.expenses_entry_detail[i].supplier_tax_id){
					frappe.throw({message:__("Please enter Supplier, Supplier Name, Supplier Tax ID for row #")+(i+1), 
					title: __("Mandatory Supplier Details.")});
				}				
				else if (!frm.doc.expenses_entry_detail[i].supplier){
					frappe.throw({message:__("Please enter Supplier for row #")+(i+1), 
					title: __("Mandatory Supplier Details.")});
				}				
				else if (!frm.doc.expenses_entry_detail[i].supplier_name){
					frappe.throw({message:__("Please enter Supplier Name for row #")+(i+1), 
					title: __("Mandatory Supplier Details.")});
				}
				else if (!frm.doc.expenses_entry_detail[i].supplier_tax_id){
					frappe.throw({message:__("Please enter Supplier Tax ID for row #")+(i+1), 
					title: __("Mandatory Supplier Details.")});
				}								

			}
		}
	}
	},	
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('View Accounting Ledger'), function () {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			});
		}
	},
	company: function (frm) {
		if (frm.doc.company) {
			frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_company_defaults",
				args: {
					company: frm.doc.company
				},
				callback: function (r, rt) {
					if (r.message) {
						console.log(r.message)
						let default_cost_center = r.message["cost_center"]
						frm.set_value("cost_center", default_cost_center || '');


					}
				}
			});
		}
	},
	check_all: function (frm) {
		var items=frm.doc.expenses_entry_detail
		for(var i=0, l=items.length; i<l; i++) {
			console.log(items[i].account_type)
			if (items[i].account_type!="tax") {
				items[i].apply_vat=1
				
			}
		}		
		frm.refresh_field('expenses_entry_detail')

	},	
	mode_of_payment: function (frm) {
		if (frm.doc.mode_of_payment && frm.doc.company) {
			frappe.call({
				method: "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account",
				args: {
					"mode_of_payment": frm.doc.mode_of_payment,
					"company": frm.doc.company
				},
				callback: function (r, rt) {
					if (r.message) {
						frm.set_value("paid_from_account", r.message.account);
					} else {
						frm.set_value("mode_of_payment", undefined);
					}
				}
			});

		}
	},
});
frappe.ui.form.on('Expenses Entry Detail', {
	expenses_entry_detail_add: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center);
	}
});
// cur_frm.set_query("cost_center", "expenses_entry_detail", function(doc, cdt, cdn) {
// 	var row = locals[cdt][cdn];
// 	frappe.model.set_value(row.doctype, row.name, 'cost_center', doc.cost_center);
// });