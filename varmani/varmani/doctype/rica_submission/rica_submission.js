// Copyright (c) 2016, Hemant Pema and contributors
// For license information, please see license.txt

frappe.ui.form.on('RICA Submission', {
	refresh: function(frm) {
        frm.add_custom_button(__("Name Verified"), function() {
//            console.log(frm.doc.first_names)
//            console.log(frm.doc.last_names)
//            console.log(frm.doc.identification_number)
//            console.log(frm.doc.customer)
//            console.log(frm.doc.name)
            frappe.call({
				method: "varmani.varmani.doctype.rica_submission.rica_submission.name_verified",
				args: {
					"first_names": frm.doc.first_names,
					"last_names": frm.doc.last_names,
					"identity_number": frm.doc.identification_number,
					'varmani_network':frm.doc.customer,
					'name':frm.doc.name
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				}
			})
        });
        frm.add_custom_button(__("Identity Number Verified"), function() {
            frappe.call({
            	method: "varmani.varmani.doctype.rica_submission.rica_submission.identity_verified",
				args: {
					'name':frm.doc.name
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				}
			})
        });
        frm.add_custom_button(__("Address Verified"), function() {
            frappe.call({
                method: "varmani.varmani.doctype.rica_submission.rica_submission.address_verified",
				args: {
					'name':frm.doc.name
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				}
			})
        });
        frm.add_custom_button(__("Rica Sims"), function() {
            frappe.call({
                method: "varmani.varmani.doctype.rica_submission.rica_submission.rica_sim",
				args: {
					'name':frm.doc.name,
					'inform_referrer':false
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
                    console.log(r);
				},
				freeze: true,
				freeze_message: 'Submitting rica application....'
			})
        });
	}
});
