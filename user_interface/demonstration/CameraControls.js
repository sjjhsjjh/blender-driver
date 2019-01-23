// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';
import Controls from './Controls.js';

export default class CameraControls extends Controls {
    constructor(userInterface) {
        super(userInterface);

        this._prefix = ['root', 'camera'];
        this._animationPath = ['animations', 'user_interface', 'camera'];
        
        this._add_panel("Zoom", ["orbitDistance"], -5.0);
        this._add_panel("Orbit", ["orbitAngle"], 0.5);
        this._add_panel("Altitude", ["worldPosition", 2], 5.0);
        this._add_panel("X", ["worldPosition", 0], 5.0);
        this._add_panel("Y", ["worldPosition", 1], 5.0);
    }

    _add_panel(text, dimension, unit) {
        const path = [...this._prefix, ...dimension];
        this._panels.push(new NumericPanel(
            this, text, path.join('_'), {
                "path":path,
                "unit":unit,
                "animationPath":this._animationPath,
                "subjectPath":this._prefix
            }));
    }
    
    show(parent) {
        const ui = this.userInterface;
        const cameraButtons = ui.append_node('div', undefined, parent);
        ui.add_button("Reset", this.reset_camera.bind(this), cameraButtons);
        ui.add_tickbox('monitorMouse', "Monitor mouse", cameraButtons);
        super.show(parent);
    }

    reset_camera() {
        const ui = this.userInterface;
        const speed = 15.0;
        this.activateInputControls(false);
        this.activateHoverControls(true);
        return this.stop(
            'reset_camera', {"animationPath": this._animationPath})
        .then(() => ui.put_cursor_subject(['root', 'floor']))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 0],
                "targetValue": 20.0,
                "subjectPath":this._prefix
            }, 'animations', 'reset_camera', 0))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 1],
                "targetValue": 1.0,
                "subjectPath":this._prefix
            }, 'animations', 'reset_camera', 1))
        .then(() => ui.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 2],
                "targetValue": 7.0,
                "subjectPath":this._prefix
            }, 'animations', 'reset_camera', 2))
        ;
    }
    
    stop(description, move) {
        return super.stop(description, move).then(() =>
            this.userInterface.fetch( "DELETE", 'animations', 'reset_camera'));
    }
}
