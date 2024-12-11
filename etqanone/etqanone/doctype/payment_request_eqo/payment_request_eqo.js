// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Request Eqo', {
	refresh:function(frm) {
		selete_party_type(frm)
		if(frm.doc.party_no){
			set_party_name(frm)
		}
		if (frm.doc.docstatus == 1 && frm.doc.pay_to == "Expense" && frm.doc.total_expense_amount > 0) {
            frm.add_custom_button(__('Create JV'), () => {
                frappe.model.open_mapped_doc({
					method: "etqanone.etqanone.doctype.payment_request_eqo.payment_request_eqo.create_jv_for_expense_payment",
					frm: frm,
				});
            });
        }

		if (frm.doc.docstatus == 1 && frm.doc.pay_to != "Expense" && frm.doc.total_payment_request_amount > 0) {
            frm.add_custom_button(__('Create Payment Entry'), () => {
				frappe.model.open_mapped_doc({
					method: "etqanone.etqanone.doctype.payment_request_eqo.payment_request_eqo.create_payment_entry",
					frm: frm,
				});
            });
        }
	},
	setup:function(frm){
		frm.set_query('cost_center', () => {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})

		frm.set_query('project', () => {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})

		frm.set_query('employee_paid_to_account', () => {
			return {
				filters: {
					account_type: "Payable",
					is_group: 0,
					company: frm.doc.company
				}
			}
		})

		frm.set_query('expense_account', 'expense_payment_request_details', () => {
			return {
				filters: {
					is_group: 0,
					root_type: "Expense",
					company: frm.doc.company
				}
			}
		})

		frm.set_query('cost_center', 'expense_payment_request_details', () => {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})

		frm.set_query('project', 'expense_payment_request_details', () => {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})


		frm.set_query('pinv_reference', 'supplier_payment_request_details', () => {
			return {
				filters: {
					status: ["in", ["Overdue", "Unpaid"]],
					supplier: frm.doc.party_no
				}
			}
		})

		frm.set_query('sinv_reference', 'customer_payment_request_details', () => {
			return {
				filters: {
					status: ["in", ["Overdue", "Unpaid"]],
					customer: frm.doc.party_no
				}
			}
		})

		frm.set_query('cost_center', 'employee_payment_request_details', () => {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})
	},
	pay_to: function(frm) {
		selete_party_type(frm)
	},
	party_no: function(frm) {
		set_party_name(frm)
	},
});

let selete_party_type = function(frm){
	if(frm.doc.pay_to === "Employee"){
		frm.set_value("party_type", "Employee")
	}
	else if(frm.doc.pay_to === "Supplier"){
		frm.set_value("party_type", "Supplier")
	}
	else if(frm.doc.pay_to === "Customer"){
		frm.set_value("party_type", "Customer")
	}
	else{
		frm.set_value("party_type", "")
	}
}

let set_party_name = function(frm){
	if(frm.doc.pay_to === "Employee"){
		frappe.db.get_value('Employee', frm.doc.party_no, 'employee_name')
			.then(r => {
			// console.log(r.message.employee_name)
			frm.set_value("party_name", r.message.employee_name)
			})
	}
	else if(frm.doc.pay_to === "Supplier"){
		frappe.db.get_value('Supplier', frm.doc.party_no, 'supplier_name')
			.then(r => {
			// console.log(r.message.supplier_name)
			frm.set_value("party_name", r.message.supplier_name)
			})
	}
	else if(frm.doc.pay_to === "Customer"){
		frappe.db.get_value('Customer', frm.doc.party_no, 'customer_name')
			.then(r => {
			// console.log(r.message.customer_name)
			frm.set_value("party_name", r.message.customer_name)
			})
	}
	else{
		frm.set_value("party_name", "")
	}
}


frappe.ui.form.on('Expense Payment Request Details Eqo', {
	expense_claim_type: function(frm, cdt, cdn){
		// frm.call('get_expense_account')
		let row = locals[cdt][cdn]
		frappe.call({
			method: "etqanone.etqanone.doctype.payment_request_eqo.payment_request_eqo.get_expense_account",
			args: {
				expense_type: row.expense_claim_type,
			},
		}).then((r) => {
			frappe.model.set_value(cdt, cdn, 'expense_account', r.message)
			console.log(r, "====expense_type")
		});
	}
})