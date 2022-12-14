# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Ol Product Custom",

    "author": "",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'sale_management','stock', 'purchase','product'
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/custom_dashboard.xml',
        'views/ol_pdc.xml',
        'data/sequence.xml',
        'views/group_product.xml',
        'report/report_view.xml',
        'report/require_thermal_report.xml',




    ],
    "images": [ ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "price": "60",
    "currency": "EUR",
}
