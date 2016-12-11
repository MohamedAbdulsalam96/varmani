// Copyright (c) 2016, Hemant Pema and contributors
// For license information, please see license.txt

frappe.ui.form.on('Varmani Network', {
	refresh: function(frm) {
        frm.add_custom_button(__("Opted In"), function() {
            //console.log('msisdn: '+ frm.doc.msisdn);
           frappe.call({
            method: "varmani.varmani.doctype.varmani_network.varmani_network.opt_in",
				args: {
					"id": frm.doc.identity_number,
					"msisdn":frm.doc.msisdn
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				}
         })
        });
        frm.add_custom_button(__("Get Upline"), function() {
            //console.log(frm.doc.name)
            frappe.call({
				method: "varmani.varmani.doctype.varmani_network.varmani_network.get_upline",
				args: {
					"name": frm.doc.name,
					"level": null
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				}
			})
        });
	}
});
