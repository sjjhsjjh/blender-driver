// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';
import Controls from './Controls.js';

export default class CursorControls extends Controls {
    constructor(userInterface) {
        super(userInterface);

        this._prefix = ['root', 'cursors', 0];
        this._animationPath = ['animations', 'user_interface', 'cursor'];

        this._add_panel("Offset", ["offset"], 1.0);
        this._add_panel("Length", ["length"], 1.0);
        this._add_panel("Radius", ["radius"], 1.0);
        this._add_panel("Rotation", ["rotation"], 0.5);
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