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
	

def make_records(path, fname):
	if os.path.isdir(path):
		import_file_by_path("{path}/{fname}".format(path=path, fname=fname))




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