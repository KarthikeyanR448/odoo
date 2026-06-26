/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { HomeMenu } from "./home_menu/home_menu";
import { patch } from "@web/core/utils/patch";
import { useBus } from "@web/core/utils/hooks";
import { router, routerBus } from "@web/core/browser/router";
import { browser } from "@web/core/browser/browser";
import { onMounted } from "@odoo/owl";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.state.homeMenuVisible = false;

        useBus(routerBus, "ROUTE_CHANGE", () => {
            this._updateHomeMenuVisibility();
        });

        useBus(this.env.bus, "TOGGLE_HOME_MENU", (ev) => {
            if (ev.detail === false) {
                this.state.homeMenuVisible = false;
            } else {
                // Navigate to root to show home menu
                browser.history.pushState({}, "", "/odoo");
                routerBus.trigger("ROUTE_CHANGE");
            }
        });

        onMounted(() => {
            this._updateHomeMenuVisibility();
        });
    },

    _updateHomeMenuVisibility() {
        const { action, model, resId, menu_id } = router.current;
        this.state.homeMenuVisible = !action && !model && !resId && !menu_id;
    },

    async _loadDefaultApp() {
        // Instead of redirecting to the first app, just show the home menu
        this.state.homeMenuVisible = true;
    },

    toggleHomeMenu(visible) {
        this.state.homeMenuVisible = (visible !== undefined) ? visible : !this.state.homeMenuVisible;
        if (this.state.homeMenuVisible) {
            browser.history.pushState({}, "", "/odoo");
            routerBus.trigger("ROUTE_CHANGE");
        }
    }
});

WebClient.components = {
    ...WebClient.components,
    HomeMenu,
};
