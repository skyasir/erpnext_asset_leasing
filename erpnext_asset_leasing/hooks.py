app_name = "erpnext_asset_leasing"
app_title = "Asset Leasing"
app_publisher = "Yasir Shaikh"
app_description = "Equipment and plant hire lifecycle for ERPNext"
app_email = "erp.yasirshaikh@gmail.com"
app_license = "mit"
app_home = "/desk/asset-leasing"

add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/erpnext_asset_leasing/images/asset_leasing.svg",
		"title": app_title,
		"route": app_home,
		"has_permission": "erpnext_asset_leasing.setup.permissions.check_app_permission",
	}
]

# Fail fast on a bare Frappe site rather than half-installing.
required_apps = ["erpnext"]

after_install = "erpnext_asset_leasing.setup.install.after_install"

# Re-applies the al_ custom fields idempotently, so a core upgrade that drops a
# column self-heals on the next migrate.
after_migrate = "erpnext_asset_leasing.setup.install.after_migrate"

# Custom Fields, Roles and Workflows ship as fixtures, so the whole
# configuration moves with the app. Reports, print formats, notifications,
# number cards, dashboard charts, the dashboard and the workspace are standard
# records in the module folder, which bench migrate syncs on its own.
# Nothing is ever created through the user interface.
#
# Custom DocPerm is deliberately NOT a fixture. Frappe ignores standard DocPerm
# for any DocType that has even one Custom DocPerm row, so importing only the
# Leasing rows would strip Accounts Manager and Accounts User off Sales Invoice.
# setup_permissions() owns those rows instead and runs from both after_install
# and after_migrate; it calls frappe.permissions.add_permission, which copies
# the standard rows in first.
WORKFLOWS = ["Rental Agreement Approval", "Rental Return Inspection", "Rental Downtime Approval"]
WORKFLOW_STATES = ["Draft", "Pending", "Approved", "Rejected", "Pending Inspection", "Damage Assessed", "Inspected"]
WORKFLOW_ACTIONS = [
	"Submit for Approval", "Approve", "Reject", "Revise",
	"Send for Inspection", "Pass Inspection", "Record Damage", "Approve Charges",
]

fixtures = [
	{"dt": "Role", "filters": [["role_name", "like", "Leasing %"]]},
	{"dt": "Custom Field", "filters": [["fieldname", "like", "al_%"]]},
	{"dt": "Workflow", "filters": [["name", "in", WORKFLOWS]]},
	{"dt": "Workflow State", "filters": [["name", "in", WORKFLOW_STATES]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", WORKFLOW_ACTIONS]]},
]

# Handlers on shared DocTypes return immediately when the document has nothing
# to do with equipment hire, so they cost nothing elsewhere on the site.
doc_events = {
	"Asset": {"validate": "erpnext_asset_leasing.events.asset.validate"},
	"Item": {"validate": "erpnext_asset_leasing.events.item.validate"},
	"Customer": {"validate": "erpnext_asset_leasing.events.customer.validate"},
	"Sales Invoice": {
		"validate": "erpnext_asset_leasing.events.sales_invoice.validate",
		"on_submit": "erpnext_asset_leasing.events.sales_invoice.on_submit",
		"on_cancel": "erpnext_asset_leasing.events.sales_invoice.on_cancel",
	},
	"Asset Repair": {
		"validate": "erpnext_asset_leasing.events.asset_repair.validate",
		"on_update": "erpnext_asset_leasing.events.asset_repair.on_update",
		"on_submit": "erpnext_asset_leasing.events.asset_repair.on_submit",
		"after_delete": "erpnext_asset_leasing.events.asset_repair.after_delete",
	},
	"Asset Movement": {
		"validate": "erpnext_asset_leasing.events.asset_movement.validate",
		"before_cancel": "erpnext_asset_leasing.events.asset_movement.before_cancel",
	},
	"Payment Entry": {
		"validate": "erpnext_asset_leasing.rental.deposits.validate",
		"on_submit": "erpnext_asset_leasing.rental.deposits.on_submit",
		"on_cancel": "erpnext_asset_leasing.rental.deposits.on_cancel",
	},
}

scheduler_events = {
	"daily": [
		"erpnext_asset_leasing.tasks.flag_overdue_returns",
		"erpnext_asset_leasing.tasks.scan_compliance_expiry",
		"erpnext_asset_leasing.tasks.refresh_utilisation_cache",
		"erpnext_asset_leasing.tasks.reconcile_asset_status",
	],
}

# Form behaviour only. Loaded per DocType rather than app-wide so these scripts
# are not parsed on every page. No Client Script records are ever created.
doctype_js = {
	"Asset": "public/js/asset.js",
	"Item": "public/js/item.js",
	"Customer": "public/js/customer.js",
	"Sales Invoice": "public/js/sales_invoice.js",
	"Quotation": "public/js/quotation.js",
	"Payment Entry": "public/js/payment_entry.js",
	"Subscription": "public/js/subscription.js",
}

# Hire documents reachable from the machine and from the invoice.
override_doctype_dashboards = {
	"Asset": "erpnext_asset_leasing.dashboards.asset",
}

jinja = {
	"methods": [
		"erpnext_asset_leasing.utils.jinja.al_duration",
		"erpnext_asset_leasing.utils.jinja.al_condition_changed",
		"erpnext_asset_leasing.utils.jinja.al_pricing_basis",
	],
}
