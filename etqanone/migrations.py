import frappe
from frappe.modules.import_file import import_file_by_path
from frappe.utils import get_bench_path
import os
from os.path import join


def after_migrations():
	if(not frappe.db.exists("Company-default_employee_petty_cash_payable_account_cf")):
		fname="custom_field.json"
		import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/etqanone/etqanone/import_records')
		make_records(import_folder_path,fname)
	after_migrate_create_si_records()	
	after_migrate_create_customer_supplier_link_fields()
	after_migrate_create_payment_request_ref_field_in_jv_and_pe()
	

def make_records(path, fname):
	if os.path.isdir(path):
		import_file_by_path("{path}/{fname}".format(path=path, fname=fname))



def after_migrate_create_customer_supplier_link_fields():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
	custom_fields = {
		"Customer": [
			dict(
				fieldname="_reference_cf",
				label="Customer Code",
				fieldtype="Data",
				insert_after="customer_name_in_arabic",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1
			),			
			dict(
				fieldname="is_linked_with_supplier_cf",
				label="Is Linked With Supplier?",
				fieldtype="Check",
				insert_after="represents_company",
				is_custom_field=1,
				is_system_generated=0,
				allow_on_submit=1,
				translatable=0,
				no_copy=1
			),
			dict(
				fieldname="linked_customer_supplier_cf",
				label="Linked Supplier",
				fieldtype="Link",
				options="Supplier",
				insert_after="is_linked_with_supplier_cf",
				is_custom_field=1,
				is_system_generated=0,
				allow_on_submit=1,
				translatable=0,
				no_copy=1,
				depends_on= "eval:doc.is_linked_with_supplier_cf==1"
			)            
		]        
	}
	print("Creating custom fields for app Etqanone:")
	for dt, fields in custom_fields.items():
		print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
	create_custom_fields(custom_fields)	

def after_migrate_create_si_records():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_field

	create_custom_field(
		"Sales Invoice",
		dict(
			fieldname="accounts_receivable_summary_cf_sb",
			label="Accounts Receivable Summary",
			fieldtype="Section Break",
			insert_after="remarks",
		),
	)
	create_custom_field(
		"Sales Invoice",
		dict(
			fieldname="accounts_receivable_summary_cf",
			label="",
			fieldtype="Long Text",
			insert_after="accounts_receivable_summary_cf_sb",
		),
	)
	frappe.db.commit()		


def after_migrate_create_payment_request_ref_field_in_jv_and_pe():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
	custom_fields = {
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
	print("Creating Payment Request Reference in Journal Entry and Payment Entry...")
	for dt, fields in custom_fields.items():
		print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
	create_custom_fields(custom_fields)	
