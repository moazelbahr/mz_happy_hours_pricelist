import { ProductPricelist } from "@point_of_sale/app/models/product_pricelist";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

patch(ProductPricelist.prototype, {
    /**
     * Extend the rule selection to honor the recurring-daily happy-hours window
     * (start_hour / end_hour), configured on each pricelist item.
     *
     * Mirrors the backend `_is_applicable_for` override:
     *   - both hours empty (0.0)  -> rule is always active (time dimension)
     *   - start <= end            -> active when now is within [start, end[
     *   - start > end             -> overnight window, active when now >= start or now < end
     *
     * Rules filtered out here are skipped, letting the next matching rule apply,
     * exactly like an expired date_start/date_end validity period is skipped below.
     */
    findBestRule(rules, quantity) {
        const now = DateTime.now();
        const minutes = now.hour * 60 + now.minute;
        const filtered = rules.filter((rule) => {
            if (rule.date_start && rule.date_start > now) {
                return false;
            }
            if (rule.date_end && rule.date_end < now) {
                return false;
            }
            if (rule.start_hour || rule.end_hour) {
                const startM = Math.floor(rule.start_hour * 60);
                const endM = Math.floor(rule.end_hour * 60);
                const inside = startM <= endM
                    ? startM <= minutes && minutes < endM
                    : minutes >= startM || minutes < endM;
                if (!inside) {
                    return false;
                }
            }
            return true;
        });
        return super.findBestRule(filtered, quantity);
    },
});
