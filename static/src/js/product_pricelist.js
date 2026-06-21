import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

patch(ProductProduct.prototype, {
    getPricelistRule(pricelist, quantity) {
        const rules = !pricelist ? [] : this.cachedPricelistRules[pricelist?.id] || [];
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
        return filtered.find((rule) => !rule.min_quantity || quantity >= rule.min_quantity);
    },
});
