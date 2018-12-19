// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';
import Controls from './Controls.js';

export default class CursorControls extends Controls {
    constructor(userInterface) {
        super(userInterface);

        this._prefix = ['root', 'cursors', 0];
        this._facePath = [...this._prefix, 'axis'];
        this._animationPath = ['animations', 'user_interface', 'cursor'];
        this._axisAnimation = ['animations', 'axis'];
        
        this._face = 0;

        this._add_panel("X", ["origin", 0], 1.0);
        this._add_panel("Y", ["origin", 1], 1.0);
        this._add_panel("Z", ["origin", 2], 1.0);
 
        this._add_panel("aX", ["axis", 0], 1.0);
        this._add_panel("aY", ["axis", 1], 1.0);
        this._add_panel("aZ", ["axis", 2], 1.0);
 
        this._add_panel("Offset", ["offset"], 1.0);
        this._add_panel("Length", ["length"], 1.0);
        this._add_panel("Radius", ["radius"], 1.0);
        this._add_panel("Rotation", ["rotation"], 0.5);
    }

    show(parent) {
        const ui = this.userInterface;
        ui.get(...this._facePath)
        .then(face => {
            const panel = ui.append_node('div', undefined, parent);
            ui.add_button("<", this._change_face.bind(this), panel, -1);
            const holder = ui.add_numeric_input(null, "" + face, null, panel);
            holder.input.onchange = () => {
                this._face = holder.get_value();
                this._change_face(0);
            };
            ui.add_button(">", this._change_face.bind(this), panel, 1);
    
            super.show(parent);
        });
    }
    
    _change_face(increment) {
        this._face += increment;
        this.userInterface.fetch( "PUT", {
            "valuePath": this._facePath,
            "speed": 3.0,
            "targetValue": this._face,
        }, ...[...this._axisAnimation, 0]);
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