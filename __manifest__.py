# -*- coding: utf-8 -*-
{
    'name': "MZ Happy Hours Pricelist",
    'summary': """Add recurring daily happy-hours time windows to Odoo pricelist rules (backend and POS).""",
    'description': """
        MZ Happy Hours Pricelist
        =========================
        This module extends Odoo's standard pricelist engine with recurring daily
        "Happy Hours" time windows. For each pricelist item you can define a
        *Happy Hours Start* and *Happy Hours End*; the rule only applies during that
        time window every day.
        
        When the current time is outside the configured window, the rule is skipped
        and the next matching rule applies - exactly like an expired date validity
        period is skipped in standard Odoo.
        
        Key Features
        ------------
        * Recurring daily time windows on every pricelist item.
        * Overnight support: windows can cross midnight (e.g. 22:00 -> 02:00).
        * Works in both the Odoo backend and the Point of Sale.
        * Timezone-aware evaluation (falls back to UTC if the user has no timezone).
        * Backward compatible: leave both fields empty and the rule stays always active.
        * Native fall-through semantics; no new models or configuration screens.
        
        Typical Use Cases
        -----------------
        * Bars & restaurants running daily happy hours.
        * Lunch-special pricing in food service.
        * Late-night or shift-based pricing.
        
        Compatibility
        -------------
        * Odoo 19.0
        * Depends on ``point_of_sale``
        * Extends ``product.pricelist.item`` with two new fields: ``start_hour`` and ``end_hour``.
    """,
    'author': "MZ Apps",
    'contributors': [
        'Moaz Elbahr <moazelbahr@gmail.com>',
    ],
    'version': '19.0.1.0.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/product_pricelist_item_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'mz_happy_hours_pricelist/static/src/js/product_pricelist.js',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
