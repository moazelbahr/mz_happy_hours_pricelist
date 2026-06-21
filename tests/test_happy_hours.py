from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged, TransactionCase


@tagged('post_install')
class TestHappyHours(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable the pricelist feature so prices are computed from pricelists.
        cls.env.user.group_ids += cls.env.ref('product.group_product_pricelist')

        cls.product = cls.env['product.product'].create({
            'name': 'Happy Hours Test Product',
            'list_price': 100.0,
            'type': 'consu',
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Happy Hours Pricelist',
            'item_ids': [Command.create({
                'applied_on': '3_global',
                'compute_price': 'fixed',
                'fixed_price': 50.0,
            })],
        })
        cls.rule = cls.pricelist.item_ids

    #--- helpers -------------------------------------------------

    def _now_local(self):
        """Current time converted to the user's timezone (naive wall-clock)."""
        return fields.Datetime.context_timestamp(self.env.user, fields.Datetime.now())

    def _price(self):
        return self.pricelist._get_product_price(self.product, 1.0)

    def _set_hours(self, start_hour, end_hour):
        self.rule.write({'start_hour': start_hour, 'end_hour': end_hour})

    #------------------------------------------------------------
    # Test cases
    #------------------------------------------------------------

    def test_01_both_empty_always_active(self):
        """Rule with no happy-hours window applies the discount at any time."""
        self._set_hours(0.0, 0.0)
        self.assertEqual(self._price(), 50.0)

    def test_02_inside_normal_window(self):
        """Rule applies when 'now' is inside a start<=end window (in user's local tz)."""
        now = self._now_local()
        start = (now.hour * 60 + now.minute) / 60.0 - 0.5   # 30 min before now
        end = (now.hour * 60 + now.minute) / 60.0 + 0.5     # 30 min after now
        self._set_hours(start, end)
        self.assertEqual(self._price(), 50.0)

    def test_03_outside_normal_window(self):
        """Rule is skipped when 'now' is outside the window; falls back to list price."""
        now = self._now_local()
        start = (now.hour * 60 + now.minute) / 60.0 + 1.0   # 1h after now
        end = (now.hour * 60 + now.minute) / 60.0 + 2.0     # 2h after now
        self._set_hours(start, end)
        self.assertEqual(self._price(), 100.0)

    def test_04_boundary_at_start(self):
        """The window is inclusive at the start (start_minute == now_minute applies)."""
        now = self._now_local()
        now_h = (now.hour * 60 + now.minute) / 60.0
        self._set_hours(now_h, now_h + (1.0 / 60.0))  # 1-minute window starting exactly now
        self.assertEqual(self._price(), 50.0)

    def test_05_boundary_at_end(self):
        """The window is exclusive at the end (now==end_minute => rule skipped)."""
        now = self._now_local()
        now_h = (now.hour * 60 + now.minute) / 60.0
        # window ends exactly at now, starts 1 minute before => now is NOT < end => skipped
        self._set_hours(now_h - (1.0 / 60.0), now_h)
        self.assertEqual(self._price(), 100.0)

    def test_06_overnight_before_midnight(self):
        """Overnight window (start>end) applies in the 'minutes >= start_m' branch.

        Construction: start is in the past (now >= start), end is further in the
        past (so start > end => overnight). 'now' satisfies minutes >= start_m.
        """
        now = self._now_local()
        now_h = (now.hour * 60 + now.minute) / 60.0
        start = now_h - 1.0       # 1h in the past  -> now >= start_m
        end = now_h - 2.0         # 2h in the past -> end < start => overnight
        self._set_hours(start, end)
        self.assertEqual(self._price(), 50.0)

    def test_07_overnight_after_midnight(self):
        """Overnight window (start>end) applies in the 'minutes < end_m' branch.

        Construction: end is slightly in the future (now < end), and start is
        much further in the future (start > end). This makes start>end (overnight),
        and 'now' satisfies the 'minutes < end_m' branch => inside.
        """
        now = self._now_local()
        now_h = (now.hour * 60 + now.minute) / 60.0
        end = now_h + 0.5     # 30 min in the future
        start = now_h + 5.0   # 5h in the future, and > end => overnight
        self._set_hours(start, end)
        self.assertEqual(self._price(), 50.0)

    def test_08_overnight_outside(self):
        """Overnight window does not apply when 'now' falls in the gap between end and start.

        Construction: start is in the future (now < start), end is in the past
        (now >= end). Both overnight branches fail => skipped.
        """
        now = self._now_local()
        now_h = (now.hour * 60 + now.minute) / 60.0
        start = now_h + 1.0       # 1h in the future -> now < start_m
        end = now_h - 1.0         # 1h in the past   -> now >= end_m
        self._set_hours(start, end)
        self.assertEqual(self._price(), 100.0)

    def test_09_user_without_timezone_falls_back_to_utc(self):
        """When the user has no tz set, context_timestamp falls back to UTC.

        We compare against UTC wall-clock to confirm the rule still works.
        """
        previous_tz = self.env.user.tz
        try:
            self.env.user.tz = False
            # Use a fresh environment so the cached env.tz is recomputed.
            env = self.env(user=self.env.user)
            now_utc = fields.Datetime.now()
            now_h = (now_utc.hour * 60 + now_utc.minute) / 60.0
            self.rule.with_env(env).write({'start_hour': now_h - 0.5, 'end_hour': now_h + 0.5})
            price = self.pricelist.with_env(env)._get_product_price(self.product, 1.0)
            self.assertEqual(price, 50.0)
        finally:
            self.env.user.tz = previous_tz
