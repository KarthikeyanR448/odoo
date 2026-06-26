/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useBus } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { routerBus } from "@web/core/browser/router";

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = this.state || useState({});
        this.state.homeMenuVisible = false;

        useBus(this.env.bus, "TOGGLE_HOME_MENU", (ev) => {
            this.state.homeMenuVisible = (ev.detail !== undefined && typeof ev.detail === 'boolean') ? ev.detail : !this.state.homeMenuVisible;
        });

        // Initialize state based on current controller
        if (this.env.bus.ACTION_MANAGER_READY) { // Optional check
            // In NavBar we might not know if we are at home yet, but the bus will trigger.
        }
    },

    _onAppsMenuClickHome() {
        console.log(window.location.href,'LLLLLLLL');
        if ((window.location.href).includes('debug=1')){
            window.location.href = "/odoo?debug=1";
        }
        else{
            window.location.href = "/odoo";
        }
    },

    // Override the default AppsMenu dropdown behavior
    onNavBarDropdownItemSelection(app) {
        super.onNavBarDropdownItemSelection(...arguments);
        this.env.bus.trigger("TOGGLE_HOME_MENU", false);
    }
});
