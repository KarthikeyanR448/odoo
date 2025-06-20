/** @odoo-module */

import { DataServiceOptions } from "@point_of_sale/app/models/data_service_options";
import { patch } from "@web/core/utils/patch";

patch(DataServiceOptions.prototype, {

    get databaseIndex() {
        const databaseTable = this.databaseTable;
        const indexes = {
            "pos.order": ["uuid"],
            "pos.order.line": ["uuid"],
            "product.product": ["barcode", "pos_categ_ids", "write_date"],
            "account.fiscal.position": ["tax_ids"],
            "product.packaging": ["barcode"],
            "stock.lot": ["name"],
            "pos.payment": ["uuid"],
            "loyalty.program": ["trigger_product_ids"],
            "calendar.event": ["appointment_resource_ids"],
            "res.partner": ["barcode"],
        };
        

        for (const model in databaseTable) {
            if (!indexes[model]) {
                indexes[model] = [databaseTable[model].key];
            } else if (!indexes[model].includes(databaseTable[model].key)) {
                indexes[model].push(databaseTable[model].key);
            }
        }

        return indexes;
    }
})
