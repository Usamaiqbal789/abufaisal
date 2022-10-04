# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Ol Product Custom",

    "author": "",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'sale_management','stock', 'purchase'
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/ol_pdc.xml',
        'reports/report.xml',
        'data/sequence.xml',
        # 'reports/ali_sale_agreement.xml',
        'reports/new_report.xml',

    ],
    "images": [ ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "price": "60",
    "currency": "EUR",
}
