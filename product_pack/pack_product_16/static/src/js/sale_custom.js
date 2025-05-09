/** @odoo-module */

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { evaluateExpr } from "@web/core/py_js/py";
import { getClassNameFromDecoration } from "@web/views/utils";
import { getCookie, setCookie } from "web.utils.cookies";
import { useService } from "@web/core/utils/hooks";

const Dialog = require('web.Dialog');

patch(ListRenderer.prototype, 'product_pack.ListRenderer', {
    setup() {
        this._super(...arguments);
        this.action = useService("action");
    },
    // function to update dragged line is a pack product and not a sub product.
    sortStop({ element }) {
        element.classList.remove("o_dragged");
        for (const cell of element.querySelectorAll("td")) {
            cell.style.width = null;
        }
        if (this.env.model.root['resModel'] == 'sale.order' && this.env.model.root['__viewType'] == 'form'){
            var class_name = element.className
            var rpc = require("web.rpc")
            var record = this.env.model.root.data['id']
            rpc.query({
                model: "sale.order",
                method: 'get_current_line',
                args: [[record],class_name],
        }).then( () =>{
            this.action.doAction({
                'type': 'ir.actions.client',
                'tag': 'soft_reload',
            });
        }, function () {
            Dialog.alert(this, _t("Error trying to connect to Odoo. Check your internet connection"));
        })
    }
},
    
    getRowClass(record) {
        var classNames = this._super(...arguments);
        
        if(record.data.is_pack===true){
            classNames = `${classNames} o_is_pack`;
        }
        return classNames;
    },
    
    getCellClass(column, record) {
        const FIELD_CLASSES = {
            char: "o_list_char",
            float: "o_list_number",
            integer: "o_list_number",
            monetary: "o_list_number",
            text: "o_list_text",
            many2one: "o_list_many2one",
        };
        
        if (!this.cellClassByColumn[column.id]) {
            const classNames = ["o_data_cell"];
            if (column.type === "button_group") {
                classNames.push("o_list_button");
            } else if (column.type === "field") {
                classNames.push("o_field_cell");
                if (
                    column.rawAttrs &&
                    column.rawAttrs.class &&
                    this.canUseFormatter(column, record)
                ) {
                    classNames.push(column.rawAttrs.class);
                }
                const typeClass = FIELD_CLASSES[this.fields[column.name].type];
                if (typeClass) {
                    classNames.push(typeClass);
                }
                if (column.widget) {
                    classNames.push(`o_${column.widget}_cell`);
                }
            }
            this.cellClassByColumn[column.id] = classNames;
        }
        const classNames = [...this.cellClassByColumn[column.id]];
        const cookie = getCookie("color_scheme"); // To get which mode (night/day) is using..!!
        if(record.data.is_pack===true){
            classNames.push("o_is_pack");
        }
        if(record.data.is_pack===true && cookie == "dark"){
            classNames.push("o_is_pack_night_mode");
            if (this.creates[0].className == "o_add_pack_control"){
                this.creates[0].className = "o_add_pack_control_dark_mode";
            }
        }
        if(record.data.hide_product===true){
            classNames.push("o_is_pack_hide");
        }
        if (column.type === "field") {
            if (record.isRequired(column.name)) {
                classNames.push("o_required_modifier");
            }
            if (record.isInvalid(column.name)) {
                classNames.push("o_invalid_cell");
            }
            if (record.isReadonly(column.name)) {
                classNames.push("o_readonly_modifier");
            }
            if (this.canUseFormatter(column, record)) {
                const { decorations } = record.activeFields[column.name];
                for (const decoName in decorations) {
                    if (evaluateExpr(decorations[decoName], record.evalContext)) {
                        classNames.push(getClassNameFromDecoration(decoName));
                    }
                }
            }
            if (
                record.isInEdition &&
                this.props.list.editedRecord &&
                this.props.list.editedRecord.isReadonly(column.name)
            ) {
                classNames.push("text-muted");
            } else {
                classNames.push("cursor-pointer");
            }
        }
        return classNames.join(" ");
    },

    onClickSortColumn(column) {
        if (this.env.model.root['resModel'] == 'sale.order' && this.env.model.root['__viewType'] == 'form'){
            return;
        }
        if (this.env.model.root['resModel'] == 'sale.order.template' && this.env.model.root['__viewType'] == 'form'){
            return;
        }
        if (this.preventReorder) {
            this.preventReorder = false;
            return;
        }
        if (this.props.list.editedRecord || this.props.list.model.useSampleModel) {
            return;
        }
        const fieldName = column.name;
        const list = this.props.list;
        if (this.isSortable(column)) {
            list.sortBy(fieldName);
        }
    },

}
)

