// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';

export default class CameraControls {
    constructor(userInterface) {
        this._userInterface = userInterface;
        this._panels = [
            new NumericPanel(this, "Zoom", ["orbitDistance"], -5.0),
            new NumericPanel(this, "Orbit", ["orbitAngle"], 0.5),
            new NumericPanel(this, "Altitude", ["worldPosition", 2], 5.0),
            new NumericPanel(this, "X", ["worldPosition", 0], 5.0),
            new NumericPanel(this, "Y", ["worldPosition", 1], 5.0)
        ];
    }
    
    get userInterface() {
        return this._userInterface;
    }
    
    show(parent) {
        const ui = this._userInterface;
        const cameraButtons = ui.append_node('div', undefined, parent);
        ui.add_button("Reset", this.reset_camera.bind(this), cameraButtons);
        ui.add_tickbox('monitorMouse', "Monitor mouse", cameraButtons);
        
        this._panels.forEach(panel => panel.show(parent));
    }

    reset_camera() {
        const speed = 15.0;
        const ui = this._userInterface;
        this.activateInputControls(false);
        this.activateHoverControls(true);
        return this.stop('reset_camera')
        .then(() => ui.put_cursor_subject(['root', 'floor']))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 0],
                "targetValue": 20.0
            }, 'animations', 'reset_camera', 0))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 1],
                "targetValue": 1.0
            }, 'animations', 'reset_camera', 1))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 2],
                "targetValue": 7.0
            }, 'animations', 'reset_camera', 2))
        ;
    }
    
    stop(moveDescription) {
        const ui = this._userInterface;
        if (ui.formValues.monitorMouse) {
            ui.monitor_add(moveDescription);
        }
        return ui.fetch("DELETE", 'animations', 'user_interface', 'camera')
        .then(() => ui.fetch("DELETE", 'animations', 'reset_camera'));
    }

    move(moveDescription, dimension, amount) {
        const ui = this._userInterface;
        if (ui.formValues.monitorMouse) {
            ui.monitor_add(moveDescription + " " + JSON.stringify(dimension));
        }
        return ui.fetch( "PUT", {
                "valuePath": ["root", "camera", ...dimension],
                "speed": amount
            }, 'animations', 'user_interface', 'camera');
    }

    get(dimension) {
        return this._userInterface.get('root', 'camera', ...dimension);
    }
    
    set(value, amount, dimension) {
        return this._userInterface.fetch( "PUT", {
                "valuePath": ["root", "camera", ...dimension],
                "speed": amount,
                "targetValue": value,
            }, 'animations', 'user_interface', 'camera');
    }
    
    name(dimension) {
        return ['camera', ...dimension].join('_');
    }
    
    activateInputControls(active) {
        this._panels.forEach(panel => panel.inputActive = active);
    }
    activateHoverControls(active) {
        this._panels.forEach(panel => panel.hoverActive = active);
    }
}
