# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = "0.0.1"

import frappe


def after_migrate():
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
