// Copyright (c) 2016, Hemant Pema and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Pins', {
	refresh: function(frm) {
        frm.add_custom_button(__("Load Pins"), function() {
            //console.log('msisdn: '+ frm.doc.msisdn);
           frappe.call({
            method: "varmani.varmani.doctype.bulk_pins.bulk_pins.load_pins",
				args: {
				},
				callback: function(r) {
					//frappe.model.sync(r.message);
					//frm.refresh();
					//console.log(r.message);
				},
				freeze: true,
				freeze_message: 'Creating Pins....'
         })
        });
	}
});
