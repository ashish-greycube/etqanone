from __future__ import unicode_literals

import frappe
import frappe.defaults
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate
from frappe.utils import (cint, split_emails, get_request_site_address, cstr,get_files_path, get_backups_path, get_url, encode)
from frappe import _
from frappe.sessions import Session


# @frappe.whitelist()
# def import_arabic_translation():
# 	configure_app()
# 	frappe.db.sql('delete from `tabTranslation`')
# 	# from frappe.core.doctype.data_import.data_import import import_file_by_path
# 	from frappe.core.doctype.data_import.data_import import import_file
# 	import_file(doctype='Translation', file_path=frappe.utils.get_bench_path()+'/apps/etqanone/etqanone/public/translation/Translation.csv', import_type="Insert", submit_after_import=False, console=False)
# 	# import_file(path=frappe.utils.get_bench_path()+'/apps/etqanone/etqanone/public/translation/Translation.csv',ignore_links=False, overwrite=True,submit=False, pre_process=None, no_email=True)


# def on_session_creation(login_manager):
# 	info = frappe.db.get_value("User", frappe.local.session_obj.user,
# 			["home_page_link"], as_dict=1)

# 	frappe.local.response["home_page"] = info.home_page_link or "/desk#home-page"

# def add_remark_in_journal_entry_account(self,method):
# 	gl_entry=[]
# 	gl_entry=frappe.get_list('GL Entry', filters={'voucher_no': self.name}, fields=['name', 'remarks', 'account'])
# 	for d in gl_entry:
# 		for jv_acct in self.get("accounts"):
# 			if ((jv_acct.account==d.account) and (jv_acct.remark)):
# 				gl_matched_entry = frappe.get_doc('GL Entry', d.name)
# 				gl_matched_entry.flags.ignore_permissions = 1
# 				df = frappe.get_meta('GL Entry').get_field("remarks")
# 				df.allow_on_submit = 1
# 				gl_matched_entry.remarks=jv_acct.remark
# 				gl_matched_entry.save()

# 				df = frappe.get_meta('GL Entry').get_field("remarks")
# 				df.allow_on_submit = 0


def configure_app():
	disable_registration()
	disable_marketplace()
	# configure_email()
	configure_systemsettings()
	

def configure_domain():
	try:
		email_account = frappe.new_doc("Email Domain")
		email_account.email_server = "imap.gmail.com"
		email_account.email_id = "notifications@flexsofts.com"
		email_account.domain_name = "flexsofts.com"
		email_account.smtp_server = "smtp.mailgun.org"
		email_account.smtp_port = int("587")
		email_account.use_imap = int(1)
		email_account.use_ssl = int(1)
		email_account.tls = int(1)
		email_account.attachment_limit = int(1)
		email_account.save()
	except frappe.DuplicateEntryError:
		frappe.clear_messages()        

def configure_account():
	try:
		email_account = frappe.get_doc("Email Account","Notifications")
		email_account.email_account_name = "Notifications"
		email_account.email_id ="notifications@flexsofts.com"
		email_account.email_server = "imap.gmail.com"
		email_account.enable_outgoing = 1
		email_account.enable_incoming = 0
		email_account.default_outgoing = 1
		email_account.login_id_is_different = 1
		email_account.login_id = "postmaster@mg.flexsofts.com"
		email_account.smtp_port = 587
		email_account.password = "39a65b2f680bc2e71fc2d5a56c7feb44-80bfc9ce-520217db"
		email_account.domain = "flexsofts.com"
		email_account.email_sync_option = "UNSEEN"
		email_account.smtp_server = "smtp.mailgun.org"
		email_account.use_imap = 1
		email_account.use_tls = 1
		email_account.use_ssl = 1
		email_account.save()
	except frappe.DuplicateEntryError:
		frappe.clear_messages()        

def configure_email():
	configure_domain()
	configure_account()


def disable_registration():
	doc = frappe.get_doc("Website Settings")
	doc.disable_signup = int(1)
	doc.save()

def disable_marketplace():
	doc = frappe.get_doc("Marketplace Settings")
	doc.disable_marketplace = int(1)
	doc.save()

def configure_systemsettings():
	gdoc = frappe.get_doc("Global Defaults")
	doc = frappe.get_doc("System Settings")
	if hasattr(gdoc,'default_company'):
		doc.email_footer_address  = gdoc.default_company
	doc.disable_standard_email_footer = int(1)
	doc.hide_footer_in_auto_email_reports = int(1)
	doc.save()




def on_submit_sales_invoice(doc, method):
    if doc.meta.get_field("accounts_receivable_summary_cf"):
        template = "etqanone/etqanone/print_format/accounts_receivable_summary.html"
        from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
            execute,
        )

        filters = dict(
            ageing_based_on="Posting Date",
            company=doc.company,
            customer=doc.customer,
            report_date=doc.posting_date,
            range1=30,
            range2=60,
            range3=90,
            range4=120,
        )

        _, summary = execute(filters)
        summary = [summary[0]] if summary else []
        accounts_receivable_summary_cf = frappe.render_template(
            template, dict(summary=summary, doc=doc)
        )
        doc.db_set("accounts_receivable_summary_cf", accounts_receivable_summary_cf)