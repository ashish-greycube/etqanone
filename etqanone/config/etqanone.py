from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
	return [
		{
			"label": _("Advance Tools"),
			"items": [
				{
					"type": "doctype",
					"name": "Administrative Decision",
					"label": _("Electronic Archive"),
					"description": _("Electronic Archive"),
					"hide_count": False
				},
				{
					"type": "doctype",
					"name": "Admin Document Type",
					"label": _("Admin Document Type"),
					"description": _("Admin Document Type"),
					"hide_count": False
				}
			]
		},
			{
			"label": _("Quick Accounts"),
			"icon": "fa fa-print",
			"items": [
				{
					"type": "doctype",
					"name": "Expense Entry",
					"label": _("Expense Entry"),
					"description": _("Expense Entry"),
					"hide_count": False
				}
			]
		},
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "General Ledger Middle East",
					"is_query_report": True,
					"doctype": "GL Entry"
				}
			]
		}		
    ]
