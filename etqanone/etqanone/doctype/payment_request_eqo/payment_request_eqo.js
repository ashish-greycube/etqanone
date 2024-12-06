// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Request Eqo', {
	refresh:function(frm) {
		selete_party_type(frm)
		if(frm.doc.party_no){
			set_party_name(frm)
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
					status: ["in", ["Overdue", "Unpaid"]]
				}
			}
		})

		frm.set_query('sinv_reference', 'customer_payment_request_details', () => {
			return {
				filters: {
					status: ["in", ["Overdue", "Unpaid"]]
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