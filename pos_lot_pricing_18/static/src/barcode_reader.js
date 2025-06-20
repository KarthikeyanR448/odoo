/** @odoo-module */

import { BarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_service";
import { patch } from "@web/core/utils/patch";

patch(BarcodeReader.prototype, {

    async _scan(code) {
        if (!code) {
            return;
        }

        const cbMaps = this.exclusiveCbMap ? [this.exclusiveCbMap] : [...this.cbMaps];

        let parseBarcode;
        try {
            parseBarcode = this.parser.parse_barcode(code);
            if (
                Array.isArray(parseBarcode) &&
                !parseBarcode.some((element) => element.type === "product")
            ) {
                throw new GS1BarcodeError("The GS1 barcode must contain a product.");
            }
        } catch (error) {
            if (this.fallbackParser && error instanceof GS1BarcodeError) {
                parseBarcode = this.fallbackParser.parse_barcode(code);
            } else {
                throw error;
            }
        }
        if (!Array.isArray(parseBarcode)) {
            parseBarcode = [parseBarcode]
        }
        if (Array.isArray(parseBarcode)) {
            cbMaps.map((cb) => cb.gs1?.(parseBarcode));
        } else {
            const cbs = cbMaps.map((cbMap) => cbMap[parseBarcode.type]).filter(Boolean);
            if (cbs.length === 0) {
                this.showNotFoundNotification(parseBarcode);
            }
            for (const cb of cbs) {
                await cb(parseBarcode);
            }
        }
    }
})
