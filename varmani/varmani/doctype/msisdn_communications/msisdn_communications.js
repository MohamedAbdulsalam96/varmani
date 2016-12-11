
frappe.ui.form.on("MSISDN Communications", "refresh", function(frm) {
    frm.add_custom_button(__("Ban MSISDN"), function() {
        //console.log(frm.doc.msisdn);
        if (frm.doc.msisdn != undefined){
            frm.doc.banned = true;
            frm.doc.banned_on = frappe.datetime.get_today();
            frm.refresh();
            console.log(frm.doc);
        }
    });
});