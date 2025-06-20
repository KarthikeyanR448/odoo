/** @odoo-module */

import { EditListInput } from "@point_of_sale/app/store/select_lot_popup/edit_list_input/edit_list_input";
import { patch } from "@web/core/utils/patch";

patch(EditListInput.prototype, {

    DisplayValue() {
        return this.props.item.text.slice(0,5);
    }
})
