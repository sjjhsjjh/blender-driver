// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';
import Controls from './Controls.js';

export default class CursorControls extends Controls {
    constructor(userInterface) {
        super(userInterface);

        this._prefix = ['root', 'cursors', 0];
        this._animationPath = ['animations', 'user_interface', 'cursor'];
        this._axisAnimation = ['animations', 'axis'];
        
        this._axisOptions = [
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, -1.0],
            [0.0, -1.0, 0.0],
            [-1.0, 0.0, 0.0]
        ];
        this._axisSelected = 0;

        this._add_panel("X", ["origin", 0], 1.0);
        this._add_panel("Y", ["origin", 1], 1.0);
        this._add_panel("Z", ["origin", 2], 1.0);
        this._add_panel("Offset", ["offset"], 1.0);
        this._add_panel("Length", ["length"], 1.0);
        this._add_panel("Radius", ["radius"], 1.0);
        this._add_panel("Rotation", ["rotation"], 0.5);
    }

    show(parent) {
        this.userInterface.add_button("Axis", this._next_axis.bind(this), parent);
        super.show(parent);
    }
    
    _next_axis() {
        this._axisSelected = (this._axisSelected + 1) % this._axisOptions.length;
        const axis = this._axisOptions[this._axisSelected];
        for(let index=0; index < axis.length; index++) {
            this.userInterface.fetch( "PUT", {
                "valuePath": [...this._prefix, 'axis', index],
                "speed": 0.5,
                "targetValue": axis[index],
            }, ...[...this._axisAnimation, index]);
        }
    }

    _add_panel(text, dimension, unit) {
        const path = [...this._prefix, ...dimension];
        this._panels.push(new NumericPanel(
            this, text, path.join('_'), {
                "path":path,
                "unit":unit,
                "animationPath":this._animationPath
            }));
    }
    
}