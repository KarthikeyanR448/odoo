/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class HomeMenu extends Component {
    static template = "web_enterprise.HomeMenu";
    static props = {
        onAppClick: { type: Function, optional: true },
    };

    setup() {
        this.menuService = useService("menu");
        this.state = useState({
            displayedApps: [],
        });

        onWillStart(async () => {
            this._updateApps();
        });
    }

    _updateApps() {
        this.state.displayedApps = this.menuService.getApps();
    }

    async _onAppClick(app) {
        if (this.props.onAppClick) {
            this.props.onAppClick(app);
        }
        await this.menuService.selectMenu(app);
    }
}
