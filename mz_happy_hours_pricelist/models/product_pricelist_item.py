from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    start_hour = fields.Float(
        string="Happy Hours Start",
        digits=(16, 2),
        help="Recurring daily start time for this rule, in 24h float format "
             "(e.g. 12.5 = 12:30, 22.0 = 22:00).\n"
             "Leave empty (both fields) to make the rule always active, "
             "just like an empty validity period.\n"
             "If start > end (e.g. 22:00 -> 02:00) the window wraps around midnight.",
    )
    end_hour = fields.Float(
        string="Happy Hours End",
        digits=(16, 2),
        help="Recurring daily end time for this rule, in 24h float format "
             "(e.g. 13.0 = 13:00, 2.5 = 02:30).",
    )

    def _is_in_happy_hours(self, date):
        """Return whether the given datetime falls inside the daily happy-hours window.

        Mirrors the semantics of date_start/date_end: when both hours are empty
        (0.0 / unset) the rule is considered always active for the time dimension.
        Supports overnight windows where start_hour > end_hour (e.g. 22:00 -> 02:00).
        """
        self.ensure_one()
        if not self.start_hour and not self.end_hour:
            return True
        minutes = date.hour * 60 + date.minute
        start_m = int(self.start_hour * 60)
        end_m = int(self.end_hour * 60)
        if start_m <= end_m:
            return start_m <= minutes < end_m
        return minutes >= start_m or minutes < end_m

    def _load_pos_data_fields(self, config):
        # Extend the field list shipped to the POS so the frontend can apply the
        # recurring happy-hours window when selecting the best rule (see JS patch).
        res = super()._load_pos_data_fields(config)
        if 'start_hour' not in res:
            res.append('start_hour')
        if 'end_hour' not in res:
            res.append('end_hour')
        return res

    def _is_applicable_for(self, product, qty_in_product_uom):
        """Extend the applicability check with the recurring daily happy-hours window.

        The core method already evaluates min_quantity, applied_on (category/product/
        variant). We add the happy-hours check here so the rule is skipped (and the
        next matching rule is tried) whenever 'now' is outside the configured window,
        exactly mirroring how an expired validity period excludes the rule.
        """
        res = super()._is_applicable_for(product, qty_in_product_uom)
        if not res:
            return False
        # The user configures happy-hours in their own wall-clock time, but
        # fields.Datetime.now() returns a naive UTC value. Convert to the
        # user's timezone so the hour/minute comparison matches what they
        # configured. Falls back to UTC when the user has no tz set.
        now_user = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return self._is_in_happy_hours(now_user)
