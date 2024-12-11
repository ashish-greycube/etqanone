import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	print("Creating Payment Request Reference Payment Entry...")
	custom_field = {
		"Payment Entry": [	
			dict(
                fieldname="custom_payment_request_reference",
                label="Payment Request Reference",
                fieldtype="Link",
                options="Payment Request Eqo",
                insert_after="reference_no",
                read_only=1,
                is_custom_field=1,
                is_system_generated=0,
                translatable=0
            )		
		],
		"Journal Entry": [	
			dict(
                fieldname="custom_payment_request_reference",
                label="Payment Request Reference",
                fieldtype="Link",
                options="Payment Request Eqo",
                insert_after="reference",
                read_only=1,
                is_custom_field=1,
                is_system_generated=0,
                translatable=0
            )		
		]
	}
	
	create_custom_fields(custom_field, update=True)