// Copyright (c) 2016, Hemant Pema and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commission Structure', {
	refresh: function(frm) {

	},
	item: function(frm) {
        console.log('select:' + frm.doc.item)
    },
    last_sell_price: function(frm){
        cur_frm.set_value("gross_profit", frm.doc.last_sell_price-frm.doc.last_buy_price);
        update_network_profit(frm.doc.commission_levels);
    },
    last_buy_price: function(frm){
        cur_frm.set_value("gross_profit", frm.doc.last_sell_price-frm.doc.last_buy_price);
        update_network_profit(frm.doc.commission_levels);
    }
});

update_network_profit = function(levels){
            var sum=0;
            levels.forEach(function(itm){
                if(itm.is_percentage){
                    //console.log(itm)
//                    console.log(cur_frm.get_field("last_sell_price").value*itm.amount/100)
                    sum+=(cur_frm.get_field("last_sell_price").value*itm.amount/100)
                }
                else{
                    sum+=itm.amount;
                }

            });
            cur_frm.set_value("profits_to_network", sum);
        }