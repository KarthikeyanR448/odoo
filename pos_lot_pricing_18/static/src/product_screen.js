import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {

    async _barcodeGS1Action(parsed_results) {
        const productBarcode = parsed_results.find((element) => element.type === "product");
        const lotBarcode = parsed_results.find((element) => element.type === "lot");
        
        let product
        if (productBarcode){
            product = await this._getProductByBarcode(productBarcode);
        }
        if (lotBarcode){
            
            product = await this._getProductByBarcode(lotBarcode);
        }

        if (!product) {
            this.barcodeReader.showNotFoundNotification(
                parsed_results.find((element) => element.type === "product")
            );
            return;
        }
        
        if (product && parsed_results) {
            const lot_result = await rpc("/web/dataset/call_kw", {
                model: "stock.lot",
                method: "get_lot_values",
                args: [[],parsed_results[0]['base_code']],
                kwargs: {},
            });
            let pos_record = this.pos.data.records['pos.order.line']
            
            let existing_qty = 0
            for (let record of pos_record){
                if (record[1].product_id.tracking === "lot"){
                    let lot_name =record[1].pack_lot_ids[0]['lot_name']
                    if (lot_name == lot_result['lot_name']){
                        existing_qty += 1;
                }
                }
            }
            if (existing_qty < lot_result['quantity']){
                await this.pos.addLineToCurrentOrder({ product_id: product }, { code: lotBarcode });
            }
            else{
                this.notification.add(
                    _t(
                        "The product with specific LOT number is out of stock."
                    ),
                    {
                        type: "warning",
                        title: _t(`Unknown Barcode Quantity`) + " " + parsed_results[0]['base_code'],
                    }
                );
            }
        }
        
        this.numberBuffer.reset();
    },

    async _getProductByBarcode(code) {
        let product = this.pos.models["product.product"].getBy("barcode", code.base_code);        
        
        if (!product) {
            const productPackaging = this.pos.models["product.packaging"].getBy(
                "barcode",
                code.base_code
            );
            product = productPackaging && productPackaging.product_id;
        }

        if (!product) {
            const productlot = this.pos.models["stock.lot"].getBy(
                "name",
                code.base_code
            );
            product = productlot && productlot.product_id;
        }

        if (!product) {
            const records = await this.pos.data.callRelated(
                "pos.session",
                "find_product_by_barcode",
                [odoo.pos_session_id, code.base_code, this.pos.config.id]
            );
            await this.pos.processProductAttributes();

            if (records && records["product.product"].length > 0) {
                product = records["product.product"][0];
                await this.pos._loadMissingPricelistItems([product]);
            }
        }

        return product;
    }
})