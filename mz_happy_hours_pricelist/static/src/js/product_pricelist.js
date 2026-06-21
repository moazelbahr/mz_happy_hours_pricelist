/** @odoo-module */

import { Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Product.prototype, {
    isPricelistItemUsable(item, date) {
        if (!super.isPricelistItemUsable(item, date)) {
            return false;
        }
        if (item.start_hour || item.end_hour) {
            const minutes = date.hour * 60 + date.minute;
            const startM = Math.floor(item.start_hour * 60);
            const endM = Math.floor(item.end_hour * 60);
            const inside = startM <= endM
                ? startM <= minutes && minutes < endM
                : minutes >= startM || minutes < endM;
            if (!inside) {
                return false;
            }
        }
        return true;
    },
});
