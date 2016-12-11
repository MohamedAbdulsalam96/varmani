// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// tree of chart of accounts / cost centers
// multiple companies
// add node
// edit node
// see ledger

frappe.pages["network-browser"].on_page_load  = function(wrapper){
	frappe.ui.make_app_page({
		parent: wrapper,
		title:"Varmani Network",
		single_column: true
	})

	frappe.breadcrumbs.add("Varmani");

	var main = wrapper.page.main,
		chart_area = $("<div>")
			.css({"margin-bottom": "15px", "min-height": "200px"})
			.appendTo(main),
		help_area = $('<hr><div style="padding: 0px 15px;">'+
		'<h4>'+__('Quick Help')+'</h4>'+
		'<ol>'+
			'<li>'+__('To add child nodes, explore tree and click on the node under which you want to add more nodes.')+
		'</ol>'+
		'</div>').appendTo(main);

	if (frappe.boot.user.can_create.indexOf("Company") !== -1) {
		wrapper.page.add_menu_item(__('New Company'), function() { newdoc('Company'); }, true);
	}

	wrapper.page.add_menu_item(__('Refresh'), function() {
			wrapper.$company_select.change();
		});

	wrapper.page.set_primary_action(__('New'), function() {
		erpnext.varmani_network && erpnext.varmani_network.make_new();
	}, "octicon octicon-plus");

	// company-select
	wrapper.$company_select = wrapper.page.add_select("Company", [])
		.change(function() {
			//console.log('ctype ---- :', frappe.get_route()[1])
			var ctype = frappe.get_route()[1] || 'Varmani Network';
			erpnext.varmani_network = new erpnext.VarmaniNetwork(ctype, $(this).val(), chart_area.get(0), wrapper.page);
		})

	// load up companies
	return frappe.call({
		method: 'varmani.varmani.page.network_browser.network_browser.get_companies',
		callback: function(r) {
			wrapper.$company_select.empty();
			console.log("r: " ,r);
			$.each(r.message, function(i, v) {
				console.log(v);
				$('<option>').html(v).attr('value', v).appendTo(wrapper.$company_select);
			});
			wrapper.$company_select.val(frappe.defaults.get_user_default("Company") || r.message[0]).change();
		}
	});
}

frappe.pages["network-browser"].on_page_show = function(wrapper){
	// set route
	var ctype = frappe.get_route()[1] || 'Varmani Network';

	if(erpnext.varmani_network && erpnext.varmani_network.ctype != ctype) {
		wrapper.$company_select.change();
	}
}

erpnext.VarmaniNetwork = Class.extend({
	init: function(ctype, company, wrapper, page) {
		$(wrapper).empty();
		var me = this;
		me.ctype = ctype;
		me.can_create = frappe.model.can_create(this.ctype);
		me.can_delete = frappe.model.can_delete(this.ctype);
		me.can_write = frappe.model.can_write(this.ctype);
		me.page = page;
		//me.set_title();

		// __("Accounts"), __("Cost Centers")
		me.company = company;

		this.tree = new frappe.ui.Tree({
			parent: $(wrapper),
			label: ctype,//==="Varmani Network",// ? "Accounts" : "Cost Centers",
			args: {ctype: me.ctype, comp: me.company},
			method: 'varmani.varmani.page.network_browser.network_browser.get_children',
			click: function(link) {
				// bold
				$('.bold').removeClass('bold'); // deselect
				$(link).parent().find('.balance-area:first').addClass('bold'); // select
				console.log("Click");
				frappe.set_route("Form", "Varmani Network", node.data.value);
			},
			toolbar: [
				{ toggle_btn: true },
				{
					label: __("Open"),
					condition: function(node) {
						return node.data.full_name;
						 },
					click: function(node, btn) {
						 frappe.set_route("Form", me.ctype, node.label);
					}
				},
				{
					condition: function(node) { return true; },
					label: __("Add Child"),
					click: function() {
						me.make_new()
					}
				},
				{
					label: __("View Ledger"),
					click: function(node, btn) {
						frappe.route_options = {
							"account": node.label,
							"from_date": sys_defaults.year_start_date,
							"to_date": sys_defaults.year_end_date,
							"company": me.company
						};
						frappe.set_route("query-report", "General Ledger");
					}
				},
				{
					label: __("Rename"),
					click: function(node) {
						frappe.model.rename_doc(me.ctype, node.label, function(new_name) {
							node.reload_parent();
						});
					}
				},
				{
					condition: function(node) { return !node.root && me.can_delete },
					label: __("Delete"),
					click: function(node) {
						frappe.model.delete_doc(me.ctype, node.label, function() {
							node.parent.remove();
						});
					},
					btnClass: "hidden-xs"
				}
			],
			onrender: function(node) {
				console.log("on render: " , node);
				me.id = node.data.value;
			},
			get_label: function(node) {
				console.log("get_label: ", node.data.full_name);
				if (node.data.full_name){
					return node.data.full_name;
				}
				else
				{
					return ctype;
				}

			}
		});
	},

	make_new: function() {
		if(this.ctype=='Varmani Network') {
			this.new_customer();
		}
	},

	new_customer: function() {
		var me = this;

		var node = me.tree.get_selected_node();
		console.log("Selected node is : ", node);
		if(!(node && node.expandable)) {
			frappe.msgprint(__("Select a group node first."));
			return;
		}

		//newdoc('Varmani Network');

		// the dialog
		var d = new frappe.ui.Dialog({
			title:__('New Varmani Network Customer'),
			fields: [
				{fieldtype:'Data', fieldname:'account_name', label:__('New Account Name'), reqd:true,
					description: __("Name of new Account. Note: Please don't create accounts for Customers and Suppliers")},
				{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
					description: __('Further accounts can be made under Groups, but entries can be made against non-Groups')},
				{fieldtype:'Select', fieldname:'root_type', label:__('Root Type'),
					options: ['Asset', 'Liability', 'Equity', 'Income', 'Expense'].join('\n'),
				},
				{fieldtype:'Select', fieldname:'account_type', label:__('Account Type'),
					options: ['', 'Bank', 'Cash', 'Warehouse', 'Tax', 'Chargeable'].join('\n'),
					description: __("Optional. This setting will be used to filter in various transactions.") },
				{fieldtype:'Float', fieldname:'tax_rate', label:__('Tax Rate')},
				{fieldtype:'Link', fieldname:'warehouse', label:__('Warehouse'), options:"Warehouse"},
				{fieldtype:'Link', fieldname:'account_currency', label:__('Currency'), options:"Currency",
					description: __("Optional. Sets company's default currency, if not specified.")}
			]
		})

		var fd = d.fields_dict;

		// root type if root
		$(fd.root_type.wrapper).toggle(node.root);

		// create
		d.set_primary_action(__("Create New"), function() {
			var btn = this;
			var v = d.get_values();
			if(!v) return;

			var node = me.tree.get_selected_node();
			v.parent_account = node.label;
			v.company = me.company;

			if(node.root) {
				v.is_root = true;
				v.parent_account = null;
			} else {
				v.is_root = false;
				v.root_type = null;
			}

			return frappe.call({
				args: v,
				method: 'varmani.varmani.utils.add_ac',
				callback: function(r) {
					d.hide();
					if(node.expanded) {
						node.toggle_node();
					}
					node.load();
				}
			});
		});

		// show
		d.on_page_show = function() {
			$(fd.is_group.input).change();
			$(fd.account_type.input).change();
		}

		$(fd.is_group.input).prop("checked", false).change();
		d.show();
	}
});
