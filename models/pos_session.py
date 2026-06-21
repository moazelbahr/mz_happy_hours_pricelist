from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _product_pricelist_item_fields(self):
        res = super()._product_pricelist_item_fields()
        if 'start_hour' not in res:
            res.append('start_hour')
        if 'end_hour' not in res:
            res.append('end_hour')
        return res
