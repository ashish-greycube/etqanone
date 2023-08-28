// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Administrative Decision', {
	refresh: function(frm) {

	},
	trans_type:function(frm) {
		if (frm.doc.trans_type=='Received Document') {
			frm.set_value("naming_series", 'AD-IN-');
			frm.refresh_field('naming_series');
		} else if(frm.doc.trans_type=='Sent Document'){
			frm.set_value("naming_series", 'AD-OUT-');
			frm.refresh_field('naming_series');
		}		
		else if(frm.doc.trans_type=='Inside Document'){
			frm.set_value("naming_series", 'AD-INSIDE-');
			frm.refresh_field('naming_series');
		}
	}
});
